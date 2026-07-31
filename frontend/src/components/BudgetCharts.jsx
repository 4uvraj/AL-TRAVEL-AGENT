import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const COLORS = ['#6366f1', '#06b6d4', '#f59e0b', '#10b981'];

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(15,23,42,0.95)',
        border: '1px solid rgba(99,102,241,0.3)',
        borderRadius: '8px',
        padding: '8px 12px',
        fontSize: '0.8rem',
        color: '#e2e8f0',
      }}>
        <p style={{ margin: 0, fontWeight: 600 }}>{payload[0].name}</p>
        <p style={{ margin: 0, color: payload[0].color || '#6366f1' }}>
          ₹{parseFloat(payload[0].value).toLocaleString()}
        </p>
      </div>
    );
  }
  return null;
};

export default function BudgetCharts({ budget, days }) {
  if (!budget || !budget.grand_total) return null;

  const pieData = [
    { name: 'Accommodation', value: budget.accommodation_total || 0 },
    { name: 'Food', value: budget.food_total || 0 },
    { name: 'Transport', value: budget.transport_total || 0 },
    { name: 'Activities', value: budget.activities_total || 0 },
  ].filter(d => d.value > 0);

  const barData = (days || []).map((d, i) => ({
    name: `Day ${d.day || i + 1}`,
    cost: d.day_total || 0,
  }));

  return (
    <div className="charts-section animate-fadeInUp" style={{
      display: 'grid',
      gridTemplateColumns: barData.length > 0 ? '1fr 1fr' : '1fr',
      gap: '16px',
    }}>
      {/* Donut Chart */}
      <div style={{
        padding: '20px',
        borderRadius: 'var(--radius-lg)',
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
      }}>
        <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: '8px' }}>
          📊 Budget Breakdown
        </h4>
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%" cy="50%"
              innerRadius={55} outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {pieData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '0.72rem', color: '#94a3b8' }}
              iconType="circle"
              iconSize={8}
            />
          </PieChart>
        </ResponsiveContainer>
        <div style={{ textAlign: 'center', marginTop: '-10px' }}>
          <span style={{
            fontFamily: "'Space Grotesk', sans-serif",
            fontSize: '1.1rem', fontWeight: 700,
            background: 'linear-gradient(135deg, #6366f1, #06b6d4)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            ₹{parseFloat(budget.grand_total).toLocaleString()}
          </span>
          <span style={{ fontSize: '0.7rem', color: '#64748b', display: 'block' }}>Total Budget</span>
        </div>
      </div>

      {/* Bar Chart */}
      {barData.length > 0 && (
        <div style={{
          padding: '20px',
          borderRadius: 'var(--radius-lg)',
          background: 'var(--color-surface)',
          border: '1px solid var(--color-border)',
        }}>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-text)', marginBottom: '8px' }}>
            📈 Daily Costs
          </h4>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} axisLine={false} tickLine={false}
                tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="cost" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
