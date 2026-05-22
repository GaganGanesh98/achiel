import type { Comment, Post, VoteCounts } from "@/types";

export function effectiveVote(entity: { my_vote: number; user_vote?: number | null }): number {
  if (entity.my_vote !== 0) return entity.my_vote;
  return entity.user_vote ?? 0;
}

/** Compute next vote value when user clicks up (1) or down (-1). */
export function nextVoteValue(current: number, direction: 1 | -1): number {
  return current === direction ? 0 : direction;
}

export function applyVoteToPost(post: Post, nextVote: number): Post {
  const current = effectiveVote(post);
  let { upvotes, downvotes, score } = post;

  if (current === 1) {
    upvotes -= 1;
    score -= 1;
  } else if (current === -1) {
    downvotes -= 1;
    score += 1;
  }

  if (nextVote === 1) {
    upvotes += 1;
    score += 1;
  } else if (nextVote === -1) {
    downvotes += 1;
    score -= 1;
  }

  return {
    ...post,
    upvotes,
    downvotes,
    score,
    my_vote: nextVote,
    user_vote: nextVote === 0 ? null : nextVote,
  };
}

export function applyVoteToComment<T extends Comment>(comment: T, nextVote: number): T {
  const current = effectiveVote(comment);
  let { upvotes, downvotes, score } = comment;

  if (current === 1) {
    upvotes -= 1;
    score -= 1;
  } else if (current === -1) {
    downvotes -= 1;
    score += 1;
  }

  if (nextVote === 1) {
    upvotes += 1;
    score += 1;
  } else if (nextVote === -1) {
    downvotes += 1;
    score -= 1;
  }

  return {
    ...comment,
    upvotes,
    downvotes,
    score,
    my_vote: nextVote,
  };
}

export function mergeVoteCounts<T extends Post | Comment>(
  entity: T,
  counts: VoteCounts
): T {
  const base = {
    ...entity,
    upvotes: counts.upvotes,
    downvotes: counts.downvotes,
    score: counts.score,
    my_vote: counts.my_vote,
  };
  if ("user_vote" in entity) {
    return {
      ...base,
      user_vote: counts.my_vote === 0 ? null : counts.my_vote,
    } as T;
  }
  return base as T;
}
