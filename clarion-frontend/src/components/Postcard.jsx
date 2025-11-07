import ScorePill from './ScorePill'
import ScoreChart from './ScoreChart'

export default function PostCard({ post, expanded=false }){
  const adv = post.advanced_score ?? 0
  return (
    <div className="glass p-4 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-xs uppercase opacity-60">{post.platform}</div>
          <a href={post.url} target="_blank" className="font-semibold leading-snug hover:underline">
            {post.title}
          </a>
          <div className="mt-1 text-xs opacity-70">
            Created: {post.created_at ? new Date(post.created_at).toLocaleString() : '—'}
          </div>
        </div>
        <ScorePill score={adv}/>
      </div>

      {expanded && (
        <>
          <ScoreChart post={post}/>
          <div className="text-sm opacity-80">
            <div>Credibility: {(post.credibility_score??0).toFixed(2)}</div>
            <div>Community Sentiment: {post.community_sentiment==null?'—':post.community_sentiment.toFixed(2)}</div>
          </div>
          {post.score_explanation && (
            <div className="text-xs mt-1 opacity-70">
              Reason: {post.score_explanation.reason || post.score_explanation.mode || '—'}
            </div>
          )}
        </>
      )}
    </div>
  )
}
