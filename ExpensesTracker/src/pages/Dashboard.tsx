/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import Template from "../templates/Template";
import Table from "../componenets/Table.tsx";
import Stat from "../componenets/Stat.tsx";
import { DashboardStats } from "../config/DashboardStats.ts";import CategoryPie from "../componenets/CategoryPie.tsx";
import MonthlyTrend from "../componenets/MonthlyTrend.tsx";
import { Navigate } from "react-router-dom";
import PipelineIndicator from "../componenets/PipelineIndicator.tsx";


export default function Dashboard() {
    const userId = localStorage.getItem("user_id");
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
                // Plaid path: get account/identity from Plaid via Express
                const accountRes = await fetch("/api/auth");
                const { accountNumber } = await accountRes.json();
                accountId = accountNumber;

                const idRes = await fetch("/api/identity/login");
                const id = await idRes.json();
                email = id.email;
                phone = id.phone;
            } else {
                // CSV path: get everything from our DB by user_id
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
            }
            
            const txRes = await fetch(
                `/api/account/transactions?email=${encodeURIComponent(email)}&phone=${encodeURIComponent(phone)}`
            );
            const txData = await txRes.json();
            setTransactions(txData.transactions || []);

            const statsRes = await fetch(
                `/api/account/monthly_stats?user_id=${encodeURIComponent(userId!)}&account_number=${encodeURIComponent(accountId)}`
            );
            const statsData = await statsRes.json();
            const rows = statsData.stats ?? {};

            const latest = rows[0] ?? {};
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

if (!userId) return <Navigate to="/" replace />;

    return (
        <Template >
            <div className="min-h-screen bg-base-200">
                
                {/* Header */}
                <div className="p-2 border-b-2 border-sky-900 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-sky-950 mb-3 mt-3 ml-7">
                        Dashboard
                    </h1>
                    <div className="mr-7 text-sky-950">
                        <PipelineIndicator />
                    </div>
                </div>

                <div className="p-10 w-auto">
                    {loading ? (
                        <p className="text-lg">Loading your financial data...</p>
                    ) : (
                    <>
                        {/*Stats Linear*/} 
                        <div className="flex flex-wrap justify-between gap-4 mb-8">
                            {monthlyStats && DashboardStats.map((s) => (
                                <Stat
                                key={s.title}
                                title={s.title}
                                value={(monthlyStats[s.field] ?? 0).toString()}
                                desc={s.desc}
                                />
                            ))}
                        </div>
                        
                        <div className="flex flex-wrap justify-evenly gap-5">
                            {/* Category Pie Chart */}
                            <div className="flex-1 min-w-[400px] mb-10 bg-white shadow-lg p-6 rounded-lg">
                                <h2 className="text-xl font-bold mb-4">Spending by Category</h2>
                                {categoryData.length > 0 ? (
                                    <CategoryPie data={categoryData} />
                                ) : (
                                    <p>No category data available.</p>
                                )}
                            </div>

                            {/* Monthly Trend Chart */}
                            <div className="flex-1 min-w-[400px] mb-10 bg-white shadow-lg p-6 rounded-lg">
                                <h2 className="text-xl font-bold mb-4">Monthly Spending vs Income</h2>
                                {monthlyTrendData.length > 0 ? (
                                    <MonthlyTrend data={monthlyTrendData} />
                                ) : (
                                    <p>No monthly trend data available.</p>
                                )}
                            </div>
                        </div>

                        {/* Transactions */}
                        <div className="mb-10 bg-white shadow-lg p-6 rounded-lg">
                            <h2 className="text-xl font-bold mb-1">Your Transactions</h2>
                            {loading ? (
                                <p>Loading transactions...</p>
                            ) : (
                                <Table transactions={transactions} />
                            )}
                        </div>
                    </>
                    )}
                </div>
            </div>
        </Template>
    );
}
