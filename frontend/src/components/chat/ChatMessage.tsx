import React from 'react';
import { ChatMessage as ChatMessageType, Product } from '../../types';
import { ProductCard } from '../product/ProductCard';
import { UpsellCard } from '../recommendation/UpsellCard';
import { CrossSellCard } from '../recommendation/CrossSellCard';
import { Bot, User } from 'lucide-react';

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

  return (
    <div className={`message-row ${isUser ? 'user-message' : 'agent-message'}`}>
      <div className={`avatar ${isUser ? 'avatar-user' : 'avatar-agent'}`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div className="bubble-wrapper" style={{ maxWidth: '100%' }}>
        <div className={`bubble ${isUser ? 'bubble-user' : 'bubble-agent'}`}>
          {message.text}
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

        <div className="message-timestamp">{message.timestamp}</div>
      </div>
    </div>
  );
};
