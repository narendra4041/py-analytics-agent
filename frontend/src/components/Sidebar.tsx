import type { ChatSession } from "@/lib/types";

type Props = {
  chats: ChatSession[];
  selectedChatId?: string;
  onSelectChat: (chat: ChatSession) => void;
  onNewChat: () => void;
};


export default function Sidebar({
  chats,
  selectedChatId,
  onSelectChat,
  onNewChat,
}: Props) {

  return (
    <aside className="w-72 border-r h-screen p-4">

      <h2 className="font-bold mb-4">
        Chats
      </h2>


      <button
        className="w-full mb-4 rounded bg-black text-white px-3 py-2 text-sm"
        onClick={onNewChat}
      >
        + New Chat
      </button>


      <div className="space-y-2">

        {chats.map((chat) => (

          <div
            key={chat.id}
            onClick={() => onSelectChat(chat)}
            className={`
              p-2 rounded cursor-pointer
              ${
                selectedChatId === chat.id
                  ? "bg-gray-200"
                  : "hover:bg-gray-100"
              }
            `}
          >

            <div className="font-medium">
              {chat.title}
            </div>

            <div className="text-xs text-gray-500">
              {chat.catalog}.{chat.schema}
            </div>

          </div>

        ))}

      </div>

    </aside>
  );
}