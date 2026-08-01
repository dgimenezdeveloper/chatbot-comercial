"use client";

import FacebookIcon from "@/components/icons/dashboard/facebook";
import InstagramIcon from "@/components/icons/dashboard/instagram";
import WhatsappIcon from "@/components/icons/dashboard/whatsapp";
import TwitterIcon from "@/components/icons/twitter";

import { InputWithIcon } from "@/components/ui/input-with-icon/InputWithIcon";
import { Label } from "@/components/ui/label/label";

function TiktokIcon(props) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="currentColor"
      className="size-4 text-muted-foreground"
      {...props}
    >
      <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 1 1-5.2-1.74 2.89 2.89 0 0 1 2.31-1.41V8.9a6.34 6.34 0 1 0 6.34 6.34V9.33a8.28 8.28 0 0 0 5.02 1.67V7.55a4.83 4.83 0 0 1-1.25-.86z" />
    </svg>
  );
}

const SOCIAL_FIELDS = [
  {
    name: "instagram",
    label: "Instagram",
    placeholder: "Ej. @tunegocio",
    icon: <InstagramIcon className="size-4" />,
  },
  {
    name: "facebook",
    label: "Facebook",
    placeholder: "Ej. /tunegocio",
    icon: <FacebookIcon className="size-4" />,
  },
  {
    name: "whatsapp",
    label: "WhatsApp",
    placeholder: "Ej. +54 11 2233 4455",
    icon: <WhatsappIcon className="size-4" />,
  },
  {
    name: "tiktok",
    label: "TikTok",
    placeholder: "Ej. @tunegocio",
    icon: <TiktokIcon />,
  },
  {
    name: "twitter",
    label: "X (Twitter)",
    placeholder: "Ej. @tunegocio",
    icon: <TwitterIcon className="size-4 text-muted-foreground" />,
  },
];

export default function SocialMediaFields({ data = {}, onChange }) {
  return (
    <fieldset>
      <legend className="text-sm font-medium text-foreground">
        Redes sociales{" "}
        <span className="font-normal text-muted-foreground">(opcional)</span>
      </legend>

      <div className="mt-3 space-y-3">
        {SOCIAL_FIELDS.map((social) => (
          <div key={social.name}>
            <Label htmlFor={`social-${social.name}`} className="sr-only">
              {social.label}
            </Label>
            <InputWithIcon
              id={`social-${social.name}`}
              icon={social.icon}
              value={data[social.name] ?? ""}
              onChange={(e) => onChange(social.name, e.target.value)}
              placeholder={social.placeholder}
              className="h-11"
            />
          </div>
        ))}
      </div>
    </fieldset>
  );
}