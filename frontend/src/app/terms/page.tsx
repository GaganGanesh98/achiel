import Link from "next/link";

import { LegalDraftBanner } from "@/components/legal-draft-banner";

export default function TermsPage() {
  return (
    <main className="px-4 py-12">
      <article className="prose prose-slate max-w-3xl mx-auto dark:prose-invert">
        <LegalDraftBanner>Draft terms under legal review.</LegalDraftBanner>

        <h1>Terms of Service</h1>
        <p className="text-sm text-muted-foreground not-prose">Last updated: 2026-05-22</p>

        <h2>1. Acceptance</h2>
        <p>
          By creating an account on CampusVoice, you agree to these Terms and our{" "}
          <Link href="/privacy">Privacy Policy</Link>.
        </p>

        <h2>2. Eligibility</h2>
        <ul>
          <li>18 or older.</li>
          <li>Currently enrolled at a verified university (email-domain checked).</li>
          <li>One account per person.</li>
          <li>Not based in a jurisdiction where the service is prohibited.</li>
        </ul>

        <h2>3. Your content</h2>
        <ul>
          <li>You retain ownership of what you post.</li>
          <li>
            You grant CampusVoice a non-exclusive, royalty-free, worldwide licence to display,
            host, and distribute your content within the service.
          </li>
          <li>
            You are responsible for your content. You confirm it does not infringe anyone&apos;s
            rights.
          </li>
        </ul>

        <h2>4. Acceptable use</h2>
        <p>
          <strong>You may NOT post:</strong>
        </p>
        <ul>
          <li>defamatory statements about identifiable individuals;</li>
          <li>personal data of others (names, addresses, photos without consent);</li>
          <li>threats, hate speech, slurs, or harassment;</li>
          <li>content depicting violence against persons;</li>
          <li>
            sexual content involving minors (zero tolerance, reported to authorities);
          </li>
          <li>illegal drug sales, weapon sales, or other illegal commerce;</li>
          <li>spam, advertisements, or recruitment messages;</li>
          <li>copyrighted material without permission.</li>
        </ul>
        <p>
          <strong>You may NOT use the platform to:</strong>
        </p>
        <ul>
          <li>impersonate another person;</li>
          <li>scrape or automate access without permission;</li>
          <li>attempt to compromise security or other users&apos; accounts.</li>
        </ul>

        <h2>5. Moderation</h2>
        <ul>
          <li>We may remove any content for any reason, at our discretion, with or without notice.</li>
          <li>We may suspend or terminate accounts for violations.</li>
          <li>
            Our community guidelines (
            <Link href="/community-guidelines">/community-guidelines</Link>) define what we
            remove in practice.
          </li>
        </ul>

        <h2>6. Verification</h2>
        <p>
          Account verification requires a current university email address. We may revoke
          verification if it becomes invalid.
        </p>

        <h2>7. Limitation of liability</h2>
        <ul>
          <li>The service is provided &quot;as is&quot; without warranties.</li>
          <li>
            To the maximum extent permitted by German law, our liability is limited to direct
            damages caused by gross negligence or intentional misconduct.
          </li>
          <li>
            Statutory liability under § 309 BGB and § 312 BGB remains unaffected.
          </li>
        </ul>

        <h2>8. Indemnification</h2>
        <p>
          You agree to indemnify us against third-party claims arising from your content or
          your use of the service.
        </p>

        <h2>9. Termination</h2>
        <ul>
          <li>
            You may delete your account at any time from <Link href="/me">/me</Link>.
          </li>
          <li>We may terminate your account for ToS violations.</li>
        </ul>

        <h2>10. Governing law and disputes</h2>
        <ul>
          <li>These Terms are governed by German law.</li>
          <li>Jurisdiction: Berlin, Germany.</li>
          <li>
            Consumers retain the right to bring claims in their country of residence under EU
            law.
          </li>
          <li>
            EU dispute resolution platform:{" "}
            <a
              href="https://ec.europa.eu/consumers/odr"
              target="_blank"
              rel="noopener noreferrer"
            >
              https://ec.europa.eu/consumers/odr
            </a>{" "}
            (we do not commit to participate).
          </li>
        </ul>

        <h2>11. Changes</h2>
        <p>We&apos;ll notify material changes by email at least 14 days in advance.</p>

        <h2>12. Contact</h2>
        <p>
          {`Gagan Ganesh`}, {`{{OPERATOR_ADDRESS}}`}, {`gaganganesh098@gmail.com`}
        </p>
      </article>
    </main>
  );
}
