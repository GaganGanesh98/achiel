import { LegalDraftBanner } from "@/components/legal-draft-banner";

export default function CommunityGuidelinesPage() {
  return (
    <main className="px-4 py-12">
      <article className="prose prose-slate max-w-3xl mx-auto dark:prose-invert">
        <LegalDraftBanner>
          These guidelines are a draft under legal review and may change before public launch.
        </LegalDraftBanner>

        <h1>Community Guidelines</h1>
        <p className="lead">
          What&apos;s welcome on CampusVoice, and what isn&apos;t.
        </p>

        <h2>Be respectful</h2>
        <p>
          Disagree with ideas, not people. Strong opinions are fine. Insults aren&apos;t.
        </p>

        <h2>Don&apos;t name individuals</h2>
        <ul>
          <li>
            Critique courses, programmes, facilities, policies. Don&apos;t name specific
            professors, staff, or students.
          </li>
          <li>
            If you&apos;ve been treated badly by someone, the right venue is your
            university&apos;s formal complaints process — not us.
          </li>
          <li>Posts naming individuals are removed within 24 hours of being reported.</li>
        </ul>

        <h2>No allegations of crimes</h2>
        <ul>
          <li>
            We remove posts accusing specific people of crimes (theft, harassment, assault,
            etc.) unless they reference a publicly-filed report or news article that we can
            verify.
          </li>
          <li>
            This is to protect you from defamation lawsuits and to protect potential victims
            from harm.
          </li>
        </ul>

        <h2>No personal data of others</h2>
        <p>
          Don&apos;t post anyone&apos;s full name, address, phone number, photo, or social
          media handle without their explicit consent.
        </p>

        <h2>No hate speech</h2>
        <p>
          Slurs, threats, dehumanising language targeting any group are auto-flagged and
          removed.
        </p>

        <h2>No spam or recruitment</h2>
        <p>
          No selling, no MLMs, no &quot;join my Discord/Telegram&quot;, no academic cheating
          services, no essay-writing services.
        </p>

        <h2>No NSFW</h2>
        <p>
          Sexual content, gore, and shock content are removed. This is a student forum, not a
          4chan board.
        </p>

        <h2>How moderation works</h2>
        <ul>
          <li>Anyone can report a post or comment using the flag icon.</li>
          <li>Reports go to a queue reviewed within 48 hours.</li>
          <li>We may remove content with or without explanation.</li>
          <li>Repeat violations lead to account suspension or removal.</li>
        </ul>

        <h2>Appeals</h2>
        <p>
          If your post was removed and you think it shouldn&apos;t have been, email{" "}
          {`gaganganesh098@gmail.com`}.
        </p>
      </article>
    </main>
  );
}
