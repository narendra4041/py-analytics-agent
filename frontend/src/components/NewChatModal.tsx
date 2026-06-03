"use client";

import { useEffect, useState } from "react";

import {
  createChat,
  getCatalogs,
  getSchemas,
} from "@/lib/api";

import type { ChatSession } from "@/lib/types";

type Props = {
  open: boolean;
  onClose: () => void;
  onCreated: (chat: ChatSession) => void;
};

export default function NewChatModal({
  open,
  onClose,
  onCreated,
}: Props) {
  const [title, setTitle] = useState("");
  const [catalogs, setCatalogs] = useState<string[]>([]);
  const [schemas, setSchemas] = useState<string[]>([]);
  const [catalog, setCatalog] = useState("");
  const [schema, setSchema] = useState("");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (!open) return;

    getCatalogs().then((data) => {
      setCatalogs(data.catalogs);
    });
  }, [open]);

  useEffect(() => {
    if (!catalog) return;

    getSchemas(catalog).then((data) => {
      setSchemas(data.schemas);
      setSchema("");
    });
  }, [catalog]);

  async function handleCreate() {
    if (!title || !catalog || !schema) return;

    setCreating(true);

    try {
      const chat = await createChat(
        title,
        catalog,
        schema
      );

      onCreated(chat);
      onClose();

      setTitle("");
      setCatalog("");
      setSchema("");
    } finally {
      setCreating(false);
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="bg-white rounded-lg p-6 w-96 space-y-4">
        <h2 className="text-lg font-bold">
          New Chat
        </h2>

        <input
          className="w-full border rounded px-3 py-2"
          placeholder="Chat title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <select
          className="w-full border rounded px-3 py-2"
          value={catalog}
          onChange={(e) => setCatalog(e.target.value)}
        >
          <option value="">Select catalog</option>
          {catalogs.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <select
          className="w-full border rounded px-3 py-2"
          value={schema}
          onChange={(e) => setSchema(e.target.value)}
          disabled={!catalog}
        >
          <option value="">Select schema</option>
          {schemas.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <div className="flex justify-end gap-2">
          <button
            className="px-3 py-2 rounded border"
            onClick={onClose}
          >
            Cancel
          </button>

          <button
            className="px-3 py-2 rounded bg-black text-white disabled:bg-gray-400"
            disabled={
              creating ||
              !title ||
              !catalog ||
              !schema
            }
            onClick={handleCreate}
          >
            {creating ? "Creating..." : "Create"}
          </button>
        </div>
      </div>
    </div>
  );
}