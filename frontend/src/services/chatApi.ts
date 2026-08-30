import { API_BASE_URL } from '../config/api';
import { Product, UpsellData } from '../types';

export interface ChatResponse {
  session_id: string;
  message: string;
  products?: Product[];
  crossSell?: Product[];
  upsell?: UpsellData;
}

/**
 * POST /api/chat/
 * Sends natural language shopping inquiry to the authoritative AI Commerce Agent backend.
 */
export async function sendChat(
  message: string,
  sessionId: string | null
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId || undefined,
      message,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => '');
    throw new Error(
      `Backend Chat API error (HTTP ${response.status}): ${errorText || response.statusText}`
    );
  }

  const data: ChatResponse = await response.json();
  return data;
}
