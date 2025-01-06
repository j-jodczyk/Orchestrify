import dynamic from "next/dynamic";

const PianoRollNoSSR = dynamic(() => import("../components/PianoRoll"), {
  ssr: false,
});

export default PianoRollNoSSR;
