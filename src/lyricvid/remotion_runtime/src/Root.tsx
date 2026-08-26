import React from "react";
import {Composition} from "remotion";
import {LyricVideo} from "./LyricVideo";
import {tracks} from "./tracks";

const FPS = 24;

export const RemotionRoot: React.FC = () => (
  <>
    {tracks.map((track: any) => (
      <Composition
        key={track.id}
        id={track.id}
        component={LyricVideo}
        fps={FPS}
        width={track.format === "short" ? 1080 : track.format === "square" ? 1080 : 1280}
        height={track.format === "short" ? 1920 : track.format === "square" ? 1080 : 720}
        durationInFrames={Math.max(1, Math.ceil((track.duration + Math.max(0, Number(track.introSeconds ?? 0)) + Math.max(0, Number(track.outroSeconds ?? 0))) * FPS))}
        defaultProps={{track}}
      />
    ))}
  </>
);
