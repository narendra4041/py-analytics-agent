"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import Sidebar from "@/components/Sidebar";
import ResultRenderer from "@/components/ResultRenderer";
import ChatInput from "@/components/ChatInput";
import MessageBubble from "@/components/MessageBubble";
import {
  getChats,
  getMessages,
  sendAgentMessage,
} from "@/lib/api";

import type {
  ChatMessage,
  ChatSession,
} from "@/lib/types";

import NewChatModal from "@/components/NewChatModal";

export default function Home() {
  const [chats, setChats] =
    useState<ChatSession[]>([]);

  const [selectedChat, setSelectedChat] =
    useState<ChatSession | null>(null);

  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [loading, setLoading] =
    useState(true);

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);

  const [newChatOpen, setNewChatOpen] =
    useState(false);

  const [loadingResponse, setLoadingResponse] =
  useState(false);


  useEffect(() => {
    getChats()
      .then((data) => {
        setChats(data);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);


  async function handleSelectChat(
    chat: ChatSession
  ) {
    setSelectedChat(chat);

    const chatMessages =
      await getMessages(chat.id);

    setMessages(chatMessages);
  }


  async function handleSendMessage(
    message: string
  ) {
    if (!selectedChat) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      chat_id: selectedChat.id,
      user_id: "narendra",
      role: "user",
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages((current) => [
      ...current,
      userMessage,
    ]);

    setLoadingResponse(true);

    try {

      const response = await sendAgentMessage(
        selectedChat.id,
        message
      );


      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        chat_id: selectedChat.id,
        user_id: "narendra",
        role: "assistant",
        content: response.result,
        created_at: new Date().toISOString(),
      };


      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);

    }
    finally {

      setLoadingResponse(false);

    }
  }


  return (
    <main className="flex h-screen">

      <Sidebar
        chats={chats}
        selectedChatId={selectedChat?.id}
        onSelectChat={handleSelectChat}
        onNewChat={() => setNewChatOpen(true)}
      />


      <section className="flex-1 flex flex-col">

        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold">
            {
              selectedChat
                ? selectedChat.title
                : "Py Analytics Agent"
            }
          </h1>

          <p className="mt-2 text-gray-500">
            {
              loading
                ? "Loading chats..."
                : selectedChat
                  ? `${selectedChat.catalog}.${selectedChat.schema}`
                  : "Select a chat to begin."
            }
          </p>
        </div>


        <div className="flex-1 overflow-auto p-6 space-y-3">

          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
            />
          ))}
          {loadingResponse && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl px-4 py-3 text-sm">
                Analyzing your data...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />

        </div>


        <ChatInput
          disabled={!selectedChat}
          onSend={handleSendMessage}
        />

      </section>
      <NewChatModal
        open={newChatOpen}
        onClose={() => setNewChatOpen(false)}
        onCreated={(chat) => {
          setChats((current) => [
            chat,
            ...current,
          ]);

          setSelectedChat(chat);
          setMessages([]);
        }}
      />

    </main>
  );
}