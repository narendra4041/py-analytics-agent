import type { AgentResult } from "@/lib/types";

type Props = {
  result: AgentResult;
};

export default function ResultRenderer({ result }: Props) {
  if (result.type === "text") {
    return (
      <p className="text-sm">
        {result.summary}
      </p>
    );
  }

  if (result.type === "chart") {
    console.log(
        "chart result",
        result
    );
    return (
      <div className="space-y-2">
        <p className="text-sm">
          {result.summary}
        </p>

        <img
          src={result.chart_url}
          alt={result.summary}
          className="max-w-3xl rounded border"
        />
      </div>
    );
  }

  if (result.type === "table") {
    return (
      <div className="space-y-2">
        <p className="text-sm">
          {result.summary}
        </p>

        <div className="overflow-auto rounded border">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-100">
              <tr>
                {result.columns.map((column) => (
                  <th
                    key={column}
                    className="px-3 py-2 text-left font-medium"
                  >
                    {column}
                  </th>
                ))}
              </tr>
            </thead>

            <tbody>
              {result.rows.map((row, index) => (
                <tr
                  key={index}
                  className="border-t"
                >
                  {result.columns.map((column) => (
                    <td
                      key={column}
                      className="px-3 py-2"
                    >
                      {row[column]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  }

  return null;
}