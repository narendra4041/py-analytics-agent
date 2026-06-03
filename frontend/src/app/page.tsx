"use client";

import { useEffect, useState } from "react";

import Sidebar from "@/components/Sidebar";
import ResultRenderer from "@/components/ResultRenderer";

import {
  getChats,
  getMessages,
} from "@/lib/api";

import type {
  ChatMessage,
  ChatSession,
} from "@/lib/types";


export default function Home() {
  const [chats, setChats] =
    useState<ChatSession[]>([]);

  const [selectedChat, setSelectedChat] =
    useState<ChatSession | null>(null);

  const [messages, setMessages] =
    useState<ChatMessage[]>([]);

  const [loading, setLoading] =
    useState(true);


  // runs once when page opens
  useEffect(() => {
    getChats()
      .then((data) => {
        setChats(data);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);


  async function handleSelectChat(
    chat: ChatSession
  ) {
    setSelectedChat(chat);

    const chatMessages =
      await getMessages(chat.id);

    setMessages(chatMessages);
  }


  return (
    <main className="flex h-screen">

      {/* Left sidebar */}
      <Sidebar
        chats={chats}
        selectedChatId={selectedChat?.id}
        onSelectChat={handleSelectChat}
      />


      {/* Chat area */}
      <section className="flex-1 p-6 overflow-auto">

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


        {/* Messages */}
        <div className="mt-6 space-y-3">

          {messages.map((message) => (
            <div
              key={message.id}
              className="rounded border p-3"
            >

              <div className="text-xs text-gray-500 mb-2">
                {message.role}
              </div>


              {
                message.content === null ? (
                  <p className="text-sm text-gray-400">
                    No content
                  </p>
                ) : typeof message.content === "string" ? (
                  <pre className="whitespace-pre-wrap text-sm">
                    {message.content}
                  </pre>
                ) : (
                  <ResultRenderer result={message.content} />
                )
              }

            </div>
          ))}

        </div>

      </section>

    </main>
  );
}