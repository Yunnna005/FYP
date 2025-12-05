import { useEffect, useState } from "react";
import Template from "../templates/Template";

export default function Dashboard() {
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function loadData() {
            try {
                // Fetch accounts
                const accRes = await fetch("http://localhost:8000/accounts");
                const accData = await accRes.json();
                setAccounts(accData.accounts || []);

                setLoading(false);
            } catch (error) {
                console.error("Error loading Plaid data:", error);
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
                            {/* USER ACCOUNT DETAILS */}
                            <div className="mb-10 bg-white shadow-lg p-6 rounded-lg">
                                <h2 className="text-xl font-bold mb-4">Account Details</h2>
                                
                                
                                {accounts?.length > 0 ? (
                                    <>
                                        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                                        {accounts.map((acc: any) => (
                                            <div key={acc.account_id} className="mb-4 p-4 border rounded-lg">
                                                <p><strong>Name:</strong> {acc.name}</p>
                                                <p><strong>Type:</strong> {acc.type}</p>
                                                <p><strong>Subtype:</strong> {acc.subtype}</p>
                                                <p><strong>Balance:</strong> €{acc.balances.current}</p>
                                            </div>
                                        ))}
                                    </>
                                ) : (
                                    <p>No accounts found</p>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </Template>
    );
}
