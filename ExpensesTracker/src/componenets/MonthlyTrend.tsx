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
  monthly_spend: string | number;
  monthly_received: number | string;
}

export default function MonthlyTrend({ data }: { data: MonthlyData[] }) {
  return (
    <div className="w-full h-96">
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />

          {/* Spend Line */}
          <Line
            type="monotone"
            dataKey="monthly_spend"
            stroke="#ef4444"
            strokeWidth={3}
            name="Spent"
          />

          {/* Received Line */}
          <Line
            type="monotone"
            dataKey="monthly_received"
            stroke="#224ec5"
            strokeWidth={3}
            name="Received"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}