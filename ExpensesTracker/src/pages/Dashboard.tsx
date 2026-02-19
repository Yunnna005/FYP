/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from "react";
import Template from "../templates/Template";
import Table from "../componenets/Table.tsx";


export default function Dashboard() {
    const [transactions, setTransactions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
    async function loadData() {
        try {
            const res = await fetch("/api/identity/login");
            const { email, phone } = await res.json();

            if (!email || !phone) return;

            const txRes = await fetch(
                `/api/transactions/owner?email=${encodeURIComponent(email)}&phone=${encodeURIComponent(phone)}`
            );
            const txData = await txRes.json();
            setTransactions(txData.transactions || []);
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
