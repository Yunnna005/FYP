import { Link } from 'react-router-dom';

export default function NavBar() {
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
        </ul>
    );
}