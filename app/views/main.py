from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order, OrderItem
import uuid

main = Blueprint('main', __name__)

@main.route('/')
def index():
    products = Product.query.limit(6).all()
    return render_template('index.html', products=products)

@main.route('/products')
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@main.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)

@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    cart[product_id_str] = cart.get(product_id_str, 0) + quantity
    session['cart'] = cart
    flash('已加入購物車', 'success')
    return redirect(request.referrer or url_for('main.index'))

@main.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    return render_template('cart.html', cart_items=cart_items, total=total)

@main.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = int(request.form.get('quantity', 0))
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    if quantity > 0:
        cart[product_id_str] = quantity
    else:
        cart.pop(product_id_str, None)
    session['cart'] = cart
    flash('購物車已更新', 'info')
    return redirect(url_for('main.view_cart'))

@main.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart.pop(str(product_id), None)
    session['cart'] = cart
    flash('商品已移除', 'info')
    return redirect(url_for('main.view_cart'))

@main.route('/checkout')
def checkout():
    if not current_user.is_authenticated:
        flash('請先登入才能結帳', 'warning')
        return redirect(url_for('auth.login'))
    cart = session.get('cart', {})
    if not cart:
        flash('購物車是空的', 'info')
        return redirect(url_for('main.view_cart'))
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            })
    return render_template('checkout.html', cart_items=cart_items, total=total)

@main.route('/place_order', methods=['POST'])
def place_order():
    if not current_user.is_authenticated:
        flash('請先登入', 'warning')
        return redirect(url_for('auth.login'))
    cart = session.get('cart', {})
    if not cart:
        flash('購物車是空的', 'info')
        return redirect(url_for('main.view_cart'))
    total = 0
    items_to_create = []
    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))
        if product:
            subtotal = product.price * quantity
            total += subtotal
            items_to_create.append({
                'product_id': product.id,
                'quantity': quantity,
                'price': product.price
            })
    order_number = str(uuid.uuid4()).replace('-', '')[:12]
    order = Order(
        user_id=current_user.id,
        order_number=order_number,
        total_amount=total,
        status='pending'
    )
    db.session.add(order)
    db.session.flush()
    for item in items_to_create:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price']
        )
        db.session.add(order_item)
    db.session.commit()
    session.pop('cart', None)
    flash('訂單已成功建立！', 'success')
    return redirect(url_for('main.order_detail', order_id=order.id))

@main.route('/order/<int:order_id>')
def order_detail(order_id):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('你沒有權限查看此訂單', 'danger')
        return redirect(url_for('main.index'))
    return render_template('order_detail.html', order=order)

@main.route('/orders')
def orders():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders.html', orders=user_orders)