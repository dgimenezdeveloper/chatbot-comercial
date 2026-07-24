"use client";

import FacebookIcon from "@/components/icons/dashboard/facebook";
import InstagramIcon from "@/components/icons/dashboard/instagram";
import WhatsappIcon from "@/components/icons/dashboard/whatsapp";

import { InputWithIcon } from "@/components/ui/input-with-icon/InputWithIcon";
import { Label } from "@/components/ui/label/label";

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
];

export default function SocialMediaFields({ data, onChange }) {
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
