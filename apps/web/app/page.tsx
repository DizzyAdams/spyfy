import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Hero } from "@/components/sections/Hero";
import { Features } from "@/components/sections/Features";
import { HowItWorks } from "@/components/sections/HowItWorks";
import { Comparison } from "@/components/sections/Comparison";
import { Testimonials } from "@/components/sections/Testimonials";
import { Pricing } from "@/components/sections/Pricing";
import { FAQ } from "@/components/sections/FAQ";
import { GradientMesh } from "@/components/illustrations/GradientMesh";

export default function LandingPage() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <Comparison />
        <Testimonials />
        <Pricing />
        <FAQ />

        {/* Final CTA */}
        <section className="relative mx-auto max-w-7xl px-5 pb-28">
          <div className="relative overflow-hidden rounded-3xl border border-border bg-surface-2 p-10 text-center sm:p-16">
            <GradientMesh />
            <div className="relative">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Pare de testar ofertas <span className="gradient-text">mortas</span>.
              </h2>
              <p className="mx-auto mt-4 max-w-xl text-muted">
                Descubra o que está escalando agora e tenha o funil clonado na mão em menos de um minuto.
              </p>
              <div className="mt-8 flex justify-center gap-3">
                <Link href="/#precos" className="btn btn-primary !px-6 !py-3 !text-[15px]">
                  Começar grátis <ArrowRight size={16} />
                </Link>
                <Link href="/app/feed" className="btn btn-ghost !px-6 !py-3 !text-[15px]">
                  Abrir o app
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
