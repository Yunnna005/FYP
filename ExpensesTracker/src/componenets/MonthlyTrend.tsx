import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from "recharts";
 
interface MonthlyData {
  month: string;
  monthly_spend: number;
  monthly_received: number;
}
 
export default function MonthlyTrend({ data }: { data: MonthlyData[] }) {
  return (
    <div className="w-full h-48">
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="monthly_spend"
            stroke="#ef4444"
            strokeWidth={2}
            name="Spent"
            dot={false}
          />
          <Line
            type="monotone"
            dataKey="monthly_received"
            stroke="#224ec5"
            strokeWidth={2}
            name="Received"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}