import { create } from 'zustand';

type ChatStoreState = Record<string, never>;

export const useChatStore = create<ChatStoreState>(() => ({}));
