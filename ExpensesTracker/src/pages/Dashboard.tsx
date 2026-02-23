/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import Template from "../templates/Template";
import Table from "../componenets/Table.tsx";
import Stat from "../componenets/Stat.tsx";
import { DashboardStats } from "FYP/ExpensesTracker/src/config/DashboardStats.js";


export default function Dashboard() {
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [monthlyStats, setMonthlyStats] = useState<any>(null);


    useEffect(() => {
    async function loadData() {
        try {
            const res = await fetch("/api/identity/login");
            const { email, phone } = await res.json();
            if (!email || !phone) return;

            //Get UserID
            const userRes = await fetch(
                `/api/user?email=${encodeURIComponent(email)}&phone=${encodeURIComponent(phone)}`
            );
            const { user_id } = await userRes.json();
            if (!user_id) return;

            //Get Transactions
            const txRes = await fetch(
                `/api/account/transactions?email=${encodeURIComponent(email)}&phone=${encodeURIComponent(phone)}`
            );
            const txData = await txRes.json();
            setTransactions(txData.transactions || []);

            //Get Stats
            const statsRes = await fetch(`/api/account/monthly_stats?user_id=${user_id}`);
            const statsData = await statsRes.json();
            setMonthlyStats(statsData);

            setLoading(false);
        } catch (error) {
            console.error(error);
        }
    }

    loadData();
}, []);

    return (
        <Template>
            <div className="min-h-screen bg-base-200">
                
                {/* Header */}
                <div className="p-2 border-b-2 border-sky-900">
                    <h1 className="text-2xl font-bold text-sky-950 mb-3 mt-3 ml-7">
                        Dashboard
                    </h1>
                </div>

                <div className="p-10 w-auto">
                    {loading ? (
                        <p className="text-lg">Loading your financial data...</p>
                    ) : (
                    <>
                        {/*Stats Linear*/}
                        <div className="flex flex-wrap gap-4 mb-8">
                            {monthlyStats && DashboardStats.map((s) => (
                                <Stat
                                key={s.title}
                                title={s.title}
                                value={s.format ? s.format(monthlyStats[s.field]) : `${monthlyStats[s.field]}`}
                                desc={s.desc}
                                />
                            ))}
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
