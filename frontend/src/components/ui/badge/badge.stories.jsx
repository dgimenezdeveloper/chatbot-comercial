import {
    Badge, 
    badgeVariants,} from "../../../components/ui/badge/badge.jsx";

export default  {
    title: "Component/UI/Badge",
}

export const Default = () => <Badge>Default Badge</Badge>;
export const Variant = () => <Badge className={badgeVariants({ variant: "secondary" })}>Secondary</Badge>;