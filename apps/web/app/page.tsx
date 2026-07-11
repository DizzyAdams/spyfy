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
        <section className="relative px-5 pb-28 pt-2">
          <div className="surface relative mx-auto max-w-6xl overflow-hidden rounded-3xl border-border bg-bg/40 p-10 text-center shadow-glow sm:p-16 md:p-20">
            <GradientMesh />
            <div className="relative z-10">
              <span className="chip mb-6 !text-accent">Pronto pra escalar?</span>
              <h2 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl md:text-6xl">
                Pare de testar ofertas{" "}
                <span className="gradient-text">mortas</span>.
              </h2>
              <p className="mx-auto mt-5 max-w-xl text-[15px] leading-relaxed text-muted sm:text-base">
                Descubra o que está escalando agora e tenha o funil clonado na mão em menos de um minuto.
              </p>
              <div className="mt-9 flex flex-wrap justify-center gap-3">
                <Link
                  href="/#precos"
                  className="btn btn-primary group !px-6 !py-3 !text-[15px]"
                >
                  Começar grátis{" "}
                  <ArrowRight
                    size={16}
                    className="transition-transform duration-200 group-hover:translate-x-0.5"
                  />
                </Link>
                <Link
                  href="/app/feed"
                  className="btn btn-ghost !px-6 !py-3 !text-[15px]"
                >
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
