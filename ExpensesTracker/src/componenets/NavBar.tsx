import { Link, useNavigate } from 'react-router-dom';

export default function NavBar() {
    const navigate = useNavigate();

    function handleLogout() {
        localStorage.removeItem("user_id");
        localStorage.removeItem("login_method");
        navigate("/");
    }

    return (
        <ul className="menu bg-sky-950 min-h-full w-64 p-4 gap-2">
            <p className="text-2xl font-bold p-3 mb-4 text-slate-200">Expenses Tracker</p>
            <li>
                <Link to="/dashboard" className="text-lg font-bold text-sky-100 hover:bg-sky-900">
                    Dashboard
                </Link>
            </li>
            
            <li>
                <Link to="/chat" className="text-lg font-bold text-sky-100 hover:bg-sky-900">
                    Chat
                </Link>
            </li>

            <li className="mt-auto">
                <button
                    onClick={handleLogout}
                    className="text-lg font-bold text-red-300 hover:bg-sky-900"
                >
                    Log out
                </button>
            </li>
        </ul>
    );
}