import React from 'react';
import { ChatMessage as ChatMessageType, Product } from '../../types';
import { ProductCard } from '../product/ProductCard';
import { UpsellCard } from '../recommendation/UpsellCard';
import { CrossSellCard } from '../recommendation/CrossSellCard';
import { Bot, User } from 'lucide-react';
import { PaymentButton } from '../checkout/PaymentButton';
import { useCommerceContext } from '../../context/CommerceContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';


interface ChatMessageProps {
  message: ChatMessageType;
  onViewProductDetails: (product: Product) => void;
  onAddToCart: (product: Product) => void;
  addingProductId: string | null;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onViewProductDetails,
  onAddToCart,
  addingProductId,
}) => {
  const isUser = message.sender === 'user';
  const { updateOrderStatus, addAuditLog, setOrderId } = useCommerceContext();

  return (
    <div className={`message-row ${isUser ? 'user-message' : 'agent-message'}`}>
      <div className={`avatar ${isUser ? 'avatar-user' : 'avatar-agent'}`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div className="bubble-wrapper" style={{ maxWidth: '100%' }}>
        <div className={`bubble ${isUser ? 'bubble-user' : 'bubble-agent'}`}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.text}
          </ReactMarkdown>
        </div>


        {/* Structured Product Results */}
        {message.products && message.products.length > 0 && (
          <div className="products-grid-chat">
            {message.products.map((prod) => (
              <ProductCard
                key={prod.id}
                product={prod}
                onViewDetails={onViewProductDetails}
                onAddToCart={onAddToCart}
                isAddingToCart={addingProductId === prod.id}
              />
            ))}
          </div>
        )}

        {/* Upsell Recommendation */}
        {message.upsell && message.upsell.available && (
          <UpsellCard
            upsell={message.upsell}
            onSelectUpgrade={(upgradedProduct) => onAddToCart(upgradedProduct)}
            onViewProduct={onViewProductDetails}
          />
        )}

        {/* Cross-Sell Recommendations */}
        {message.crossSell && message.crossSell.length > 0 && (
          <CrossSellCard
            products={message.crossSell}
            onAddToCart={onAddToCart}
            onViewProduct={onViewProductDetails}
            addingProductId={addingProductId}
          />
        )}

        {/* Payment UI (shown when backend/agent provides payment payload) */}
        {message.payment && (
          <div style={{ marginTop: 12 }}>
            <PaymentButton
              paymentData={message.payment}
              onPaymentSuccess={(verified) => {
                const oid = message.payment?.order_id || (message.payment as any).order_id;
                if (oid) {
                  updateOrderStatus(oid, 'paid', verified.payment_id || verified.razorpay_payment_id);
                  setOrderId(oid);
                }
                addAuditLog(
                  'Payment Verified',
                  'Backend verified Razorpay signature',
                  'Backend System',
                  `Payment ${verified.payment_id || verified.razorpay_payment_id} confirmed for order ${oid}`,
                  'completed'
                );
              }}
              onPaymentFailure={(reason) => {
                const oid = message.payment?.order_id;
                if (oid) updateOrderStatus(oid, 'payment_failed');
                addAuditLog('Payment Failed', 'Gateway declined or verification failed', 'Razorpay Gateway', reason || 'Payment failed', 'failed');
              }}
            />
          </div>
        )}

        <div className="message-timestamp">{message.timestamp}</div>
      </div>
    </div>
  );
};
