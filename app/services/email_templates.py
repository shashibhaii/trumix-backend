"""
Beautiful HTML email templates for TruMix
"""

def get_order_confirmation_template(order_data: dict) -> str:
    """Generate order confirmation email HTML"""
    
    # Build items table
    items_html = ""
    for item in order_data['items']:
        items_html += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #eee;">
                <strong>{item['name']}</strong>
                {f"<br><small style='color: #666;'>{item.get('variant_name', '')}</small>" if item.get('variant_name') else ''}
            </td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: center;">{item['quantity']}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">₹{item['price']:.2f}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;"><strong>₹{item['price'] * item['quantity']:.2f}</strong></td>
        </tr>
        """
    
    # Format address
    addr = order_data['shipping_address']
    address_html = f"{addr.get('street', '')}<br>{addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip', '')}<br>{addr.get('country', '')}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px 0;">
            <tr>
                <td align="center">
                    <!-- Main Container -->
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: 600;">TruMix</h1>
                                <p style="color: #ffffff; margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Premium Indian Snacks & Beverages</p>
                            </td>
                        </tr>
                        
                        <!-- Success Message -->
                        <tr>
                            <td style="padding: 40px 30px 20px 30px; text-align: center;">
                                <div style="background-color: #10b981; width: 60px; height: 60px; border-radius: 50%; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center;">
                                    <span style="color: white; font-size: 30px;">✓</span>
                                </div>
                                <h2 style="color: #1f2937; margin: 0 0 10px 0; font-size: 24px;">Order Confirmed!</h2>
                                <p style="color: #6b7280; margin: 0; font-size: 16px;">Thank you for your order, {order_data['customer_name']}!</p>
                            </td>
                        </tr>
                        
                        <!-- Order Info -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9fafb; border-radius: 8px; padding: 20px;">
                                    <tr>
                                        <td>
                                            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Order Number</p>
                                            <p style="margin: 0; color: #1f2937; font-size: 20px; font-weight: 600;">#{order_data['order_id']}</p>
                                        </td>
                                        <td style="text-align: right;">
                                            <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Order Date</p>
                                            <p style="margin: 0; color: #1f2937; font-size: 16px;">{order_data.get('order_date', 'Today')}</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Items Table -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <h3 style="color: #1f2937; margin: 0 0 20px 0; font-size: 18px;">Order Items</h3>
                                <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;">
                                    <thead>
                                        <tr style="background-color: #f9fafb;">
                                            <th style="padding: 12px; text-align: left; color: #6b7280; font-size: 14px; font-weight: 600;">Product</th>
                                            <th style="padding: 12px; text-align: center; color: #6b7280; font-size: 14px; font-weight: 600;">Qty</th>
                                            <th style="padding: 12px; text-align: right; color: #6b7280; font-size: 14px; font-weight: 600;">Price</th>
                                            <th style="padding: 12px; text-align: right; color: #6b7280; font-size: 14px; font-weight: 600;">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {items_html}
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Price Breakdown -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td style="padding: 8px 0; color: #6b7280; font-size: 15px;">Subtotal</td>
                                        <td style="padding: 8px 0; color: #1f2937; font-size: 15px; text-align: right;">₹{order_data['subtotal']:.2f}</td>
                                    </tr>
                                    {f'''<tr>
                                        <td style="padding: 8px 0; color: #10b981; font-size: 15px;">Discount</td>
                                        <td style="padding: 8px 0; color: #10b981; font-size: 15px; text-align: right;">-₹{order_data['discount_amount']:.2f}</td>
                                    </tr>''' if order_data['discount_amount'] > 0 else ''}
                                    <tr>
                                        <td style="padding: 8px 0; color: #6b7280; font-size: 15px;">Tax (18% GST)</td>
                                        <td style="padding: 8px 0; color: #1f2937; font-size: 15px; text-align: right;">₹{order_data['tax_amount']:.2f}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 8px 0; color: #6b7280; font-size: 15px;">Shipping</td>
                                        <td style="padding: 8px 0; color: #1f2937; font-size: 15px; text-align: right;">{f"₹{order_data['shipping_amount']:.2f}" if order_data['shipping_amount'] > 0 else '<span style="color: #10b981;">FREE</span>'}</td>
                                    </tr>
                                    {f'''<tr>
                                        <td style="padding: 8px 0; color: #6b7280; font-size: 15px;">COD Charges</td>
                                        <td style="padding: 8px 0; color: #1f2937; font-size: 15px; text-align: right;">₹{order_data['cod_charges']:.2f}</td>
                                    </tr>''' if order_data['cod_charges'] > 0 else ''}
                                    <tr style="border-top: 2px solid #e5e7eb;">
                                        <td style="padding: 15px 0 0 0; color: #1f2937; font-size: 18px; font-weight: 600;">Total</td>
                                        <td style="padding: 15px 0 0 0; color: #667eea; font-size: 24px; font-weight: 700; text-align: right;">₹{order_data['total_amount']:.2f}</td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Shipping Address -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <h3 style="color: #1f2937; margin: 0 0 15px 0; font-size: 18px;">Shipping Address</h3>
                                <div style="background-color: #f9fafb; border-radius: 8px; padding: 20px; color: #1f2937; line-height: 1.6;">
                                    <strong>{order_data['customer_name']}</strong><br>
                                    {address_html}
                                </div>
                            </td>
                        </tr>
                        
                        <!-- CTA Button -->
                        <tr>
                            <td style="padding: 0 30px 40px 30px; text-align: center;">
                                <a href="https://trumix.co.in/orders/{order_data['order_id']}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 8px; font-size: 16px; font-weight: 600;">Track Your Order</a>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Questions? Contact us at <a href="mailto:support@trumix.co.in" style="color: #667eea; text-decoration: none;">support@trumix.co.in</a></p>
                                <p style="margin: 0; color: #9ca3af; font-size: 12px;">© 2026 TruMix. All rights reserved.</p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html


def get_welcome_email_template(user_data: dict) -> str:
    """Generate welcome email HTML"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 20px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                        
                        <!-- Header with gradient -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 50px 30px; text-align: center;">
                                <h1 style="color: #ffffff; margin: 0 0 10px 0; font-size: 36px; font-weight: 700;">Welcome to TruMix!</h1>
                                <p style="color: #ffffff; margin: 0; font-size: 18px; opacity: 0.9;">Premium Indian Snacks & Beverages</p>
                            </td>
                        </tr>
                        
                        <!-- Welcome Message -->
                        <tr>
                            <td style="padding: 40px 30px 30px 30px;">
                                <h2 style="color: #1f2937; margin: 0 0 20px 0; font-size: 24px;">Hello {user_data['name']}! 👋</h2>
                                <p style="color: #4b5563; margin: 0 0 20px 0; font-size: 16px; line-height: 1.6;">
                                    We're thrilled to have you join the TruMix family! Get ready to experience the finest selection of authentic Indian snacks and beverages, delivered right to your doorstep.
                                </p>
                                <p style="color: #4b5563; margin: 0; font-size: 16px; line-height: 1.6;">
                                    Whether you're craving traditional Thekua, refreshing beverages, or discovering new flavors, we've got something special for everyone.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Special Offer Box -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 12px; padding: 30px; text-align: center;">
                                    <h3 style="color: #ffffff; margin: 0 0 15px 0; font-size: 22px; font-weight: 600;">🎉 Welcome Gift!</h3>
                                    <p style="color: #ffffff; margin: 0 0 20px 0; font-size: 16px; opacity: 0.95;">Get 10% off your first order with code:</p>
                                    <div style="background-color: rgba(255,255,255,0.2); border: 2px dashed #ffffff; border-radius: 8px; padding: 15px; display: inline-block;">
                                        <code style="color: #ffffff; font-size: 24px; font-weight: 700; letter-spacing: 2px;">WELCOME10</code>
                                    </div>
                                    <p style="color: #ffffff; margin: 20px 0 0 0; font-size: 14px; opacity: 0.9;">Valid on orders above ₹200</p>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Features Grid -->
                        <tr>
                            <td style="padding: 0 30px 30px 30px;">
                                <h3 style="color: #1f2937; margin: 0 0 25px 0; font-size: 20px; text-align: center;">Why Choose TruMix?</h3>
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td width="50%" style="padding: 0 10px 20px 0; vertical-align: top;">
                                            <div style="background-color: #f9fafb; border-radius: 8px; padding: 20px; height: 100%;">
                                                <div style="color: #667eea; font-size: 30px; margin-bottom: 10px;">🏆</div>
                                                <h4 style="color: #1f2937; margin: 0 0 10px 0; font-size: 16px;">Premium Quality</h4>
                                                <p style="color: #6b7280; margin: 0; font-size: 14px; line-height: 1.5;">Handpicked products made with authentic recipes</p>
                                            </div>
                                        </td>
                                        <td width="50%" style="padding: 0 0 20px 10px; vertical-align: top;">
                                            <div style="background-color: #f9fafb; border-radius: 8px; padding: 20px; height: 100%;">
                                                <div style="color: #667eea; font-size: 30px; margin-bottom: 10px;">🚚</div>
                                                <h4 style="color: #1f2937; margin: 0 0 10px 0; font-size: 16px;">Fast Delivery</h4>
                                                <p style="color: #6b7280; margin: 0; font-size: 14px; line-height: 1.5;">Quick and reliable delivery across India</p>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td width="50%" style="padding: 0 10px 0 0; vertical-align: top;">
                                            <div style="background-color: #f9fafb; border-radius: 8px; padding: 20px; height: 100%;">
                                                <div style="color: #667eea; font-size: 30px; margin-bottom: 10px;">💝</div>
                                                <h4 style="color: #1f2937; margin: 0 0 10px 0; font-size: 16px;">Fresh Products</h4>
                                                <p style="color: #6b7280; margin: 0; font-size: 14px; line-height: 1.5;">Always fresh, always delicious</p>
                                            </div>
                                        </td>
                                        <td width="50%" style="padding: 0 0 0 10px; vertical-align: top;">
                                            <div style="background-color: #f9fafb; border-radius: 8px; padding: 20px; height: 100%;">
                                                <div style="color: #667eea; font-size: 30px; margin-bottom: 10px;">🎁</div>
                                                <h4 style="color: #1f2937; margin: 0 0 10px 0; font-size: 16px;">Special Offers</h4>
                                                <p style="color: #6b7280; margin: 0; font-size: 14px; line-height: 1.5;">Exclusive deals and discounts</p>
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- CTA Button -->
                        <tr>
                            <td style="padding: 0 30px 40px 30px; text-align: center;">
                                <a href="https://trumix.co.in/products" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 16px 50px; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">Start Shopping</a>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                                <p style="margin: 0 0 15px 0; color: #4b5563; font-size: 14px;">Follow us for updates and special offers!</p>
                                <div style="margin-bottom: 20px;">
                                    <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 24px;">📘</a>
                                    <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 24px;">📷</a>
                                    <a href="#" style="display: inline-block; margin: 0 8px; color: #667eea; text-decoration: none; font-size: 24px;">🐦</a>
                                </div>
                                <p style="margin: 0 0 10px 0; color: #6b7280; font-size: 14px;">Need help? Contact us at <a href="mailto:support@trumix.co.in" style="color: #667eea; text-decoration: none;">support@trumix.co.in</a></p>
                                <p style="margin: 0; color: #9ca3af; font-size: 12px;">© 2026 TruMix. All rights reserved.</p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return html
