/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import Template from "../templates/Template";
import Table from "../componenets/Table.tsx";
import Stat from "../componenets/Stat.tsx";
import { DashboardStats } from "../config/DashboardStats.ts";import CategoryPie from "../componenets/CategoryPie.tsx";
import MonthlyTrend from "../componenets/MonthlyTrend.tsx";
import { Navigate, useNavigate } from "react-router-dom";
import PipelineIndicator from "../componenets/PipelineIndicator.tsx";

const STAT_ACCENTS = [
  "bg-emerald-400",
  "bg-rose-400",
  "bg-sky-400",
  "bg-violet-400",
  "bg-amber-400",
  "bg-teal-400",
];

export default function Dashboard() {
    const userId = localStorage.getItem("user_id");
    const loginMethod = localStorage.getItem("login_method");
    const isCsvUser = loginMethod === "csv";
    const navigate = useNavigate();
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [monthlyStats, setMonthlyStats] = useState<any>(null);
    const [categoryData, setCategoryData] = useState<any[]>([]);
    const [monthlyTrendData, setMonthlyTrendData] = useState<any[]>([]);


    useEffect(() => {
    if (!userId) return;
    const loginMethod = localStorage.getItem("login_method") || "csv";

    async function loadData() {
        try {
            let email: string;
            let phone: string;
            let accountId: string;

            if (loginMethod === "plaid") {
                const accountRes = await fetch("/api/auth");
                const { accountNumber } = await accountRes.json();
                accountId = accountNumber;

                const idRes = await fetch("/api/plaid/identity/login");
                const id = await idRes.json();
                email = id.email;
                phone = id.phone;

                const txRes = await fetch(
                `/api/plaid/account/transactions?email=${encodeURIComponent(email)}&phone=${encodeURIComponent(phone)}`
                );
                const txData = await txRes.json();
                setTransactions(txData.transactions || []);
            } else {
                const userRes = await fetch(`/api/account/by_user?user_id=${encodeURIComponent(userId!)}`);
                if (!userRes.ok) {
                    console.error("Failed to load user info");
                    setLoading(false);
                    return;
                }
                const userInfo = await userRes.json();
                email = userInfo.email;
                phone = userInfo.phone_number;
                accountId = userInfo.account_id;

                const txRes = await fetch(
                `/api/account/transactions?account_id=${encodeURIComponent(accountId)}`
                );
                const txData = await txRes.json();
                setTransactions(txData.transactions || []);
            }

            const statsRes = await fetch(
                `/api/account/monthly_stats?user_id=${encodeURIComponent(userId!)}&account_number=${encodeURIComponent(accountId)}`
            );
            const statsData = await statsRes.json();
            const rows = statsData.stats ?? {};

            const latest = rows[0] ?? {};
            if (latest && Object.keys(latest).length > 0) {
                latest.net_cashflow = (parseFloat(latest.total_received) || 0) + (parseFloat(latest.total_spent) || 0);
                latest.net_cashflow = latest.net_cashflow.toFixed(2);
            }
            setMonthlyStats(latest);

            if (latest.spending_by_category) {
                const categoryData = Object.entries(latest.spending_by_category).map(
                    ([category, total]) => ({ category, total: Number(total) })
                );
                setCategoryData(categoryData);
            } else {
                setCategoryData([]);
            }

            if (rows.length > 0) {
                const sortedRows = rows.sort((a: any, b: any) =>
                    new Date(a.month_start_date).getTime() - new Date(b.month_start_date).getTime()
                );
                const trendData = sortedRows.map((row: any) => ({
                    month: new Date(row.month_start_date).toLocaleString("default", {
                        month: "short",
                        year: "2-digit",
                    }),
                    monthly_spend: parseFloat(row.total_spent),
                    monthly_received: parseFloat(row.total_received),
                }));
                setMonthlyTrendData(trendData);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    }

    loadData();
}, [userId]);

async function handleDeleteData() {
    if (!userId) return;

    const loginMethod = localStorage.getItem("login_method");
    if (loginMethod !== "csv") {
        alert("Data deletion is only available for users who uploaded their own transactions.");
        return;
    }

    const confirmed = window.confirm(
        "Are you sure? This will permanently delete all your transactions, " +
        "analysis, and account data. This cannot be undone."
    );
    if (!confirmed) return;

    try {
        const res = await fetch(`/api/account/by_user?user_id=${encodeURIComponent(userId)}`, {
            method: "DELETE",
        });
        if (res.ok) {
            localStorage.removeItem("user_id");
            localStorage.removeItem("login_method");
            navigate("/");
        } else {
            alert("Failed to delete data. Please try again.");
        }
    } catch (err) {
        alert("Network error. Please try again." + err);
    }
}

if (!userId) return <Navigate to="/" replace />;

      return (
    <Template>
      <div className="min-h-screen bg-slate-50">
 
        {/*Header*/}
        <div className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center sticky top-0 z-10">
          <div>
            <h1 className="text-xl font-bold text-slate-800 leading-none">Dashboard</h1>
            <p className="text-xs text-slate-400 mt-0.5">Your financial overview</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-slate-600">
              <PipelineIndicator />
            </div>
            {isCsvUser && (
              <button
                onClick={handleDeleteData}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-rose-600 border border-rose-200 bg-rose-50 hover:bg-rose-100 transition-colors duration-150"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete my data
              </button>
            )}
          </div>
        </div>
 
        {/*Body*/}
        <div className="px-8 py-7 space-y-7">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-32 gap-4">
              <svg className="animate-spin w-8 h-8 text-sky-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              <p className="text-slate-400 text-sm">Loading your financial data...</p>
            </div>
          ) : (
            <>
              {/*Stat cards*/}
              <div className="flex flex-wrap gap-4">
                {monthlyStats &&
                  DashboardStats.map((s, i) => (
                    <Stat
                      key={s.title}
                      title={s.title}
                      value={(monthlyStats[s.field] ?? 0).toString()}
                      desc={s.desc}
                      accent={STAT_ACCENTS[i % STAT_ACCENTS.length]}
                    />
                  ))}
              </div>
 
              {/*Charts*/}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                  <h2 className="text-sm font-semibold text-slate-700 mb-4 uppercase tracking-wide">
                    Spending by Category
                  </h2>
                  {categoryData.length > 0 ? (
                    <CategoryPie data={categoryData} />
                  ) : (
                    <p className="text-slate-400 text-sm">No category data available.</p>
                  )}
                </div>
 
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                  <h2 className="text-sm font-semibold text-slate-700 mb-4 uppercase tracking-wide">
                    Monthly Spending vs Income
                  </h2>
                  {monthlyTrendData.length > 0 ? (
                    <MonthlyTrend data={monthlyTrendData} />
                  ) : (
                    <p className="text-slate-400 text-sm">No monthly trend data available.</p>
                  )}
                </div>
              </div>
 
              {/*Transactions table*/}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                <h2 className="text-sm font-semibold text-slate-700 mb-4 uppercase tracking-wide">
                  Your Transactions
                </h2>
                <Table transactions={transactions} />
              </div>
            </>
          )}
        </div>
      </div>
    </Template>
  );
}