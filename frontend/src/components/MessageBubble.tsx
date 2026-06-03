import ResultRenderer from "@/components/ResultRenderer";
import type { ChatMessage } from "@/lib/types";


type Props = {
  message: ChatMessage;
};


export default function MessageBubble({
  message,
}: Props) {

  const isUser =
    message.role === "user";


  return (
    <div
      className={`
        flex
        ${
          isUser
            ? "justify-end"
            : "justify-start"
        }
      `}
    >

      <div
        className={`
          max-w-3xl
          rounded-2xl
          px-4
          py-3
          text-sm

          ${
            isUser
              ? "bg-black text-white"
              : "bg-gray-100 text-gray-900"
          }
        `}
      >

        {
          message.content === null ? (

            <p className="text-gray-400">
              No content
            </p>

          ) : typeof message.content === "string" ? (

            <p className="whitespace-pre-wrap">
              {message.content}
            </p>

          ) : (

            <ResultRenderer
              result={message.content}
            />

          )
        }

      </div>

    </div>
  );
}