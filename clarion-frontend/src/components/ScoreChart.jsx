import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { colorForScore } from './ScorePill'

export default function ScoreChart({ post }){
  // visualize components we expose in score_explanation
  const s = post?.score_explanation || {}
  const data = [
    { name:'Comments', value: Math.max(0, (s.comment_component??0)) },
    { name:'Source', value: Math.max(0, (s.source_component??0)) },
    { name:'Fact Check', value: Math.max(0, (s.factcheck_component??0)) },
    { name:'Article Boost', value: Math.max(0, (s.article_boost??0)) },
  ]
  const col = colorForScore(post?.advanced_score ?? 0).color
  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" outerRadius={70} label>
            {data.map((_, i) => <Cell key={i} fill={col} fillOpacity={0.35 + i*0.1} />)}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
