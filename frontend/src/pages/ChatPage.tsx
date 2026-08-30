import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ChatWindow } from '../components/chat/ChatWindow';
import { Product } from '../types';
import { useCommerceContext } from '../context/CommerceContext';
import { ShoppingBag, ArrowRight, ShieldCheck, Activity } from 'lucide-react';

export const ChatPage: React.FC = () => {
  const {
    messages,
    isLoadingChat,
    sendMessage,
    addToCart,
    addingProductId,
    cart,
  } = useCommerceContext();
  const navigate = useNavigate();

  const handleViewProduct = (product: Product) => {
    navigate(`/products/${product.id}`);
  };

  const formatINR = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val);
  };

  const totalItems = cart.items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div className="app-main-layout">
      <ChatWindow
        messages={messages}
        isLoading={isLoadingChat}
        onSendMessage={sendMessage}
        onViewProductDetails={handleViewProduct}
        onAddToCart={addToCart}
        addingProductId={addingProductId}
      />

      {/* Cart Quick Sidebar (Desktop) */}
      <aside className="cart-sidebar">
        <div className="cart-header">
          <h2>
            <ShoppingBag size={18} /> Active Cart
          </h2>
          {totalItems > 0 && <span className="cart-count-pill">{totalItems} items</span>}
        </div>

        <div className="cart-items-list">
          {cart.items.length === 0 ? (
            <div className="cart-empty-state">
              <div className="cart-empty-icon">
                <ShoppingBag size={24} />
              </div>
              <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>
                Your cart is currently empty
              </p>
              <p style={{ fontSize: 12 }}>
                Ask the AI Assistant to find products or suggest complementary accessories.
              </p>
            </div>
          ) : (
            cart.items.map((item) => (
              <div key={item.cart_item_id || item.product_id} className="cart-item-card">
                <div className="cart-item-header">
                  <span className="cart-item-name">{item.product?.name || item.product_id}</span>
                </div>
                <div className="cart-item-footer">
                  <span className="cart-item-qty">Qty: {item.quantity}</span>
                  <span className="cart-item-price">{formatINR(item.unit_price * item.quantity)}</span>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="cart-footer">
          <div className="cart-summary-row">
            <span>Subtotal ({totalItems} items):</span>
            <span>{formatINR(cart.total_amount)}</span>
          </div>

          <div className="cart-summary-row total-row">
            <span>Authoritative Total:</span>
            <span style={{ color: 'var(--color-primary)' }}>{formatINR(cart.total_amount)}</span>
          </div>

          <div className="approval-notice">
            <ShieldCheck size={14} color="var(--color-success)" style={{ flexShrink: 0 }} />
            <span>AI cannot self-authorize payment. Explicit approval is required.</span>
          </div>

          {cart.items.length > 0 ? (
            <Link
              to="/cart"
              className="btn-approve-cta"
              style={{ textDecoration: 'none' }}
            >
              <span>View Cart & Checkout</span>
              <ArrowRight size={16} />
            </Link>
          ) : (
            <Link
              to="/audit"
              className="btn-card-secondary"
              style={{ justifyContent: 'center', padding: '10px', fontSize: 13, textDecoration: 'none' }}
            >
              <Activity size={15} />
              <span>View Audit Trail</span>
            </Link>
          )}
        </div>
      </aside>
    </div>
  );
};
