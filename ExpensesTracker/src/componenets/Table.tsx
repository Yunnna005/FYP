import { useState } from "react";
 
interface Transaction {
  date: Date;
  description: string;
  amount: number;
  currency_code: string;
  pending: boolean;
}
 
type TableProps = {
  transactions: Transaction[];
};
 
const PAGE_SIZE = 5;
 
export default function Table({ transactions }: TableProps) {
  const [page, setPage] = useState(1);
  const totalPages = Math.max(1, Math.ceil(transactions.length / PAGE_SIZE));
  const paginated = transactions.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
 
  return (
    <div className="flex flex-col gap-3">
 
      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-100">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-100">
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider w-10">#</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Merchant</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Date</th>
              <th className="text-right px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Amount</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Currency</th>
              <th className="text-center px-4 py-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {paginated.length > 0 ? (
              paginated.map((tx, index) => {
                const amount = Number(tx.amount);
                const isPositive = amount >= 0;
                const globalIndex = (page - 1) * PAGE_SIZE + index + 1;
                return (
                  <tr key={index} className="hover:bg-slate-50/70 transition-colors duration-100">
                    <td className="px-4 py-3.5 text-slate-300 font-medium text-xs">{globalIndex}</td>
                    <td className="px-4 py-3.5">
                      <span className="font-medium text-slate-700 truncate max-w-[220px] block">
                        {tx.description}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-slate-500 whitespace-nowrap">
                      {new Date(tx.date).toLocaleDateString("en-IE", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                      })}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <span
                        className={`font-semibold ${
                          isPositive ? "text-emerald-600" : "text-rose-500"
                        }`}
                      >
                        {isPositive ? "+" : ""}
                        {tx.currency_code === "EUR" ? "€" : tx.currency_code + " "}
                        {Math.abs(amount).toFixed(2)}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span className="text-xs font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">
                        {tx.currency_code}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span
                        className={`inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full ${
                          tx.pending
                            ? "bg-amber-50 text-amber-600"
                            : "bg-emerald-50 text-emerald-600"
                        }`}
                      >
                        <span
                          className={`w-1.5 h-1.5 rounded-full ${
                            tx.pending ? "bg-amber-400" : "bg-emerald-400"
                          }`}
                        />
                        {tx.pending ? "Pending" : "Completed"}
                      </span>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={6} className="text-center py-12 text-slate-400 text-sm">
                  No transactions found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
 
      {/* Pagination */}
      {transactions.length > 0 && (
        <div className="flex items-center justify-between px-1">
          <p className="text-xs text-slate-400">
            Showing{" "}
            <span className="font-medium text-slate-600">
              {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, transactions.length)}
            </span>{" "}
            of{" "}
            <span className="font-medium text-slate-600">{transactions.length}</span> transactions
          </p>
 
          <div className="flex items-center gap-1">
            {/* Prev */}
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
 
            {/* Page numbers */}
            {Array.from({ length: totalPages }, (_, i) => i + 1)
              .filter((p) => p === 1 || p === totalPages || Math.abs(p - page) <= 1)
              .reduce<(number | "...")[]>((acc, p, i, arr) => {
                if (i > 0 && p - (arr[i - 1] as number) > 1) acc.push("...");
                acc.push(p);
                return acc;
              }, [])
              .map((p, i) =>
                p === "..." ? (
                  <span key={`ellipsis-${i}`} className="w-8 h-8 flex items-center justify-center text-xs text-slate-400">
                    …
                  </span>
                ) : (
                  <button
                    key={p}
                    onClick={() => setPage(p as number)}
                    className={`w-8 h-8 flex items-center justify-center rounded-lg text-xs font-semibold transition-colors ${
                      page === p
                        ? "bg-sky-500 text-white shadow-sm"
                        : "border border-slate-200 text-slate-500 hover:bg-slate-50"
                    }`}
                  >
                    {p}
                  </button>
                )
              )}
 
            {/* Next */}
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}