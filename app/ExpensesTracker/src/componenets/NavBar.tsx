export default function NavBar() {
    return <ul className="menu bg-sky-950 w-auto h-screen fixed top-0 left-0 p-4 gap-5">
        <p className="text-2xl font-bold p-3 pr-7 mb-4 text-slate-200">Expenses Tracker</p>
        <li className="text-lg font-bold text-sky-100 hover:bg-sky-900"><a>Dashboard</a></li>
        <li className="text-lg font-bold text-sky-700 menu-disabled"><a>Chat</a></li>
    </ul>;
}