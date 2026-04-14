import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
 
interface CategoryData {
  category: string;
  total: number;
}
 
export default function CategoryPie({ data }: { data: CategoryData[] }) {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
 
  return (
    <div className="w-full h-48">
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={data}
            dataKey="total"
            nameKey="category"
            outerRadius={70}
            label
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}