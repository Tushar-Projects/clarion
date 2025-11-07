import clsx from 'clsx'

export function colorForScore(score=0){
  if(score >= 0.6) return { name:'Fully Legit', color:'#6C5CE7' }      // purple
  if(score >= 0.2) return { name:'Authentic', color:'#2ECC71' }        // green
  if(score > -0.3) return { name:'Medium', color:'#1D9BF0' }           // blue
  return { name:'Fake', color:'#E74C3C' }                               // red
}

export default function ScorePill({score}){
  const m = colorForScore(score)
  return (
    <span className="px-2 py-1 rounded-full text-xs font-medium" style={{background: m.color+'22', color: m.color, border:`1px solid ${m.color}66`}}>
      {m.name} ({(score??0).toFixed(2)})
    </span>
  )
}
 