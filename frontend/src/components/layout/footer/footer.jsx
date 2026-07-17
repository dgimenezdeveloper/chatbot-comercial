import FacebookIcon from "@/components/icons/facebook";
import TwitterIcon from "@/components/icons/twitter";
import InstagramIcon from "@/components/icons/instagram";

export default function Footer() {
  return (
    <footer className="w-full bg-[#e2e8f0] pt-16 pb-8 px-6 text-slate-800">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 md:gap-8 mb-16">
        <div className="flex flex-col gap-4 md:col-span-1">
          <div className="text-2xl font-bold text-slate-900">Equipo 10</div>
          <p className="text-sm text-slate-600 mb-2">
            Nuestra vision es proveer y promover las buenas herramientas y
            programas para personas y empresas.
          </p>
          <div className="flex gap-4">
            <a
              href="#"
              className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-white hover:bg-slate-900 shadow-sm transition-colors"
            >
              <FacebookIcon className="w-full h-full" />
            </a>
            <a
              href="#"
              className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-white hover:bg-slate-900 shadow-sm transition-colors"
            >
              <TwitterIcon className="w-full h-full" />
            </a>
            <a
              href="#"
              className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-white hover:bg-slate-900 shadow-sm transition-colors"
            >
              <InstagramIcon className="w-full h-full" />
            </a>
          </div>
        </div>

        {/* Links */}
        <div className="flex flex-col gap-4">
          <h4 className="font-semibold text-slate-900 mb-2">Acerca de</h4>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Como trabajamos
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Featured
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Partnership
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Business Relation
          </a>
        </div>

        <div className="flex flex-col gap-4">
          <h4 className="font-semibold text-slate-900 mb-2">Community</h4>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Events
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Blog
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Podcast
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Invite a friend
          </a>
        </div>

        <div className="flex flex-col gap-4">
          <h4 className="font-semibold text-slate-900 mb-2">Socials</h4>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Discord
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Instagram
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Twitter
          </a>
          <a href="#" className="text-sm text-slate-600 hover:text-slate-900">
            Facebook
          </a>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between pt-8 border-t border-slate-300 text-sm text-slate-600 gap-4">
        <p>©2022 Company Name. All rights reserved</p>
        <div className="flex gap-8">
          <a href="#" className="hover:text-slate-900">
            Privacy & Policy
          </a>
          <a href="#" className="hover:text-slate-900">
            Terms & Condition
          </a>
        </div>
      </div>
    </footer>
  );
}
