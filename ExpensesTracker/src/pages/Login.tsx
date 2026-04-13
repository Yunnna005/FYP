import PlaidButton from "../componenets/PlaidButton";
import { useNavigate } from "react-router-dom";

export default function Login() {
    const navigate = useNavigate();

    return (
        <div className="hero min-h-screen bg-gradient-to-r from-[#dfe2fe] via-[#b1cbfa] to-[#8e98f5]">
            <div className="hero-content text-base-content text-center p-10 bg-base-100 rounded-lg shadow-lg">
                <div className="max-w-md">
                    <h1 className="mb-1 text-5xl font-bold">Expenses Tracker</h1>
                    <p className="mb-10">
                        AI-powered expenses tracker with banking API integration
                    </p>
                    <PlaidButton />
                    <div className="divider my-6">OR</div>
                    <button
                        className="btn btn-outline btn-info w-full"
                        onClick={() => navigate("/upload")}
                    >
                        Upload your own transactions
                    </button>
                </div>
            </div>
        </div>
    );
}