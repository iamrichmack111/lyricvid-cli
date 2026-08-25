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
        width={1280}
        height={720}
        durationInFrames={Math.max(1, Math.ceil(track.duration * FPS))}
        defaultProps={{track}}
      />
    ))}
  </>
);
