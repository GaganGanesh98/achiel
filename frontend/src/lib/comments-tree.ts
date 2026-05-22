import type { Comment } from "@/types";

export type CommentNode = Comment & { children: CommentNode[] };

export function buildCommentTree(comments: Comment[]): CommentNode[] {
  const byId = new Map<string, CommentNode>();
  const roots: CommentNode[] = [];

  for (const c of comments) {
    byId.set(c.id, { ...c, children: [] });
  }

  for (const node of byId.values()) {
    if (node.parent_comment_id && byId.has(node.parent_comment_id)) {
      byId.get(node.parent_comment_id)!.children.push(node);
    } else {
      roots.push(node);
    }
  }

  const sortNodes = (nodes: CommentNode[]) => {
    nodes.sort(
      (a, b) =>
        b.score - a.score || new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );
    for (const n of nodes) sortNodes(n.children);
  };
  sortNodes(roots);

  return roots;
}
