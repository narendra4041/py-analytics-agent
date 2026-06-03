"use client";

import { useState } from "react";

type Props = {
  disabled?: boolean;
  onSend: (message: string) => Promise<void>;
};


export default function ChatInput({
  disabled,
  onSend,
}: Props) {

  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);


  async function handleSubmit() {
    if (!message.trim()) {
      return;
    }

    setSending(true);

    try {
      await onSend(message);
      setMessage("");
    }
    finally {
      setSending(false);
    }
  }


  return (
    <div className="border-t p-4 flex gap-2">

      <input
        className="flex-1 border rounded px-3 py-2"
        placeholder="Ask your data..."
        value={message}
        disabled={disabled || sending}
        onChange={(e) =>
          setMessage(e.target.value)
        }
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            handleSubmit();
          }
        }}
      />


      <button
        className="px-4 py-2 rounded bg-black text-white disabled:bg-gray-400"
        disabled={
          disabled ||
          sending ||
          !message.trim()
        }
        onClick={handleSubmit}
      >
        {sending ? "..." : "Send"}
      </button>

    </div>
  );
}