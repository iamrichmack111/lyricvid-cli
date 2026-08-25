import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {Audio, Video} from "@remotion/media";

export const LyricVideo: React.FC<any> = ({track}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const time = frame / fps;

  const accent = track.theme.accent;
  const accent2 = track.theme.accent2;

  const activeIndex = track.lines.findIndex(
    (line: any) => time >= line.start && time <= line.end + 0.18
  );

  const active = activeIndex >= 0 ? track.lines[activeIndex] : null;
  const previous = activeIndex > 0 ? track.lines[activeIndex - 1] : null;
  const next =
    activeIndex >= 0 && activeIndex + 1 < track.lines.length
      ? track.lines[activeIndex + 1]
      : null;

  const progress = Math.min(
    100,
    Math.max(0, (time / Math.max(track.duration, 0.01)) * 100)
  );

  const zoom = 1.07 + Math.sin(frame / 85) * 0.025;
  const introOpacity = interpolate(
    frame,
    [0, 10, 55, 75],
    [0, 1, 1, 0],
    {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#020306",
        color: "white",
        overflow: "hidden",
        fontFamily: "Arial, Helvetica, sans-serif",
      }}
    >
      <Audio src={staticFile(track.audio)} />

      {track.background ? (
        <Video
          src={staticFile(track.background)}
          muted
          loop
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${zoom})`,
            filter: "brightness(.27) contrast(1.25) saturate(.85)",
          }}
        />
      ) : track.cover ? (
        <Img
          src={staticFile(track.cover)}
          style={{
            position: "absolute",
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${zoom})`,
            filter: "blur(14px) brightness(.25) contrast(1.3)",
          }}
        />
      ) : null}

      <AbsoluteFill
        style={{
          background: `
            radial-gradient(circle at ${25 + Math.sin(frame / 80) * 12}% 30%, ${accent}55, transparent 34%),
            radial-gradient(circle at 75% ${65 + Math.cos(frame / 95) * 10}%, ${accent2}44, transparent 38%),
            linear-gradient(180deg, rgba(0,0,0,.18), rgba(0,0,0,.82))
          `,
        }}
      />

      <div
        style={{
          position: "absolute",
          right: -10,
          top: -70,
          fontSize: 285,
          fontWeight: 950,
          opacity: 0.045,
          letterSpacing: -25,
        }}
      >
        {String(track.index).padStart(2, "0")}
      </div>

      {Array.from({length: 24}).map((_, i) => {
        const x = (i * 73 + track.index * 11) % 100;
        const y =
          110 - ((i * 41 + frame * (0.035 + (i % 4) * 0.01)) % 115);
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${y}%`,
              width: 2 + (i % 3),
              height: 2 + (i % 3),
              borderRadius: "50%",
              background: i % 2 ? accent : accent2,
              opacity: 0.45,
              boxShadow: `0 0 12px ${i % 2 ? accent : accent2}`,
            }}
          />
        );
      })}

      <div
        style={{
          position: "absolute",
          left: "-20%",
          right: "-20%",
          bottom: -225,
          height: 510,
          opacity: 0.34,
          backgroundImage: `
            linear-gradient(${accent}33 1px, transparent 1px),
            linear-gradient(90deg, ${accent}33 1px, transparent 1px)
          `,
          backgroundSize: "55px 55px",
          transform: "perspective(460px) rotateX(63deg)",
          transformOrigin: "center bottom",
        }}
      />

      <AbsoluteFill
        style={{
          opacity: 0.08,
          background:
            "repeating-linear-gradient(0deg,transparent 0px,transparent 3px,rgba(255,255,255,.12) 4px)",
        }}
      />

      <div
        style={{
          position: "absolute",
          left: 45,
          top: 34,
          fontWeight: 800,
          fontSize: 15,
          letterSpacing: 5,
        }}
      >
        <span style={{color: accent}}>●</span>{" "}
        LYRICVID // TRACK {String(track.index).padStart(2, "0")}
      </div>

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: 80,
          opacity: introOpacity,
        }}
      >
        <div
          style={{
            fontSize: 78,
            fontWeight: 950,
            textTransform: "uppercase",
            textShadow: `0 0 18px ${accent}, 0 0 55px ${accent2}, 0 8px 30px #000`,
          }}
        >
          {track.title}
        </div>
        <div
          style={{
            color: accent,
            marginTop: 24,
            fontFamily: "monospace",
            letterSpacing: 7,
            fontSize: 15,
          }}
        >
          {track.lyricsSource ? "EXACT LYRICS // WHISPER TIMED" : "WHISPER // WORD ALIGNED"}
        </div>
      </AbsoluteFill>

      {previous && (
        <div
          style={{
            position: "absolute",
            top: "25%",
            left: 90,
            right: 90,
            textAlign: "center",
            opacity: 0.16,
            fontSize: 21,
          }}
        >
          {previous.text}
        </div>
      )}

      <AbsoluteFill
        style={{
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: "80px 65px",
        }}
      >
        {active && (
          <div style={{maxWidth: 1110}}>
            <div
              style={{
                fontSize:
                  active.text.length > 65
                    ? 43
                    : active.text.length > 45
                      ? 51
                      : 61,
                lineHeight: 1.15,
                fontWeight: 950,
                textTransform: "uppercase",
                textShadow: "0 8px 28px rgba(0,0,0,.95)",
              }}
            >
              {active.words.map((word: any, i: number) => {
                const started = time >= word.start;
                const current = time >= word.start && time <= word.end;
                const duration = Math.max(0.04, word.end - word.start);
                const wordProgress = Math.max(
                  0,
                  Math.min(1, (time - word.start) / duration)
                );

                return (
                  <span
                    key={`${word.start}-${i}`}
                    style={{
                      display: "inline-block",
                      position: "relative",
                      marginRight: 14,
                      marginBottom: 11,
                      color: current
                        ? accent
                        : started
                          ? "#fff"
                          : "rgba(255,255,255,.27)",
                      transform: current
                        ? "translateY(-5px) scale(1.06)"
                        : "scale(1)",
                      textShadow: current
                        ? `0 0 10px ${accent}, 0 0 30px ${accent}, 0 0 55px ${accent2}`
                        : undefined,
                    }}
                  >
                    {word.text}
                    {current && (
                      <span
                        style={{
                          position: "absolute",
                          left: 0,
                          bottom: -6,
                          width: `${wordProgress * 100}%`,
                          height: 3,
                          background: accent,
                          boxShadow: `0 0 10px ${accent}`,
                        }}
                      />
                    )}
                  </span>
                );
              })}
            </div>

            {next && (
              <div style={{marginTop: 30, fontSize: 25, opacity: 0.28}}>
                {next.text}
              </div>
            )}
          </div>
        )}
      </AbsoluteFill>

      <div
        style={{
          position: "absolute",
          left: 45,
          bottom: 46,
          display: "flex",
          alignItems: "flex-end",
          gap: 4,
          height: 40,
        }}
      >
        {Array.from({length: 16}).map((_, i) => {
          const v = Math.abs(
            Math.sin(frame * 0.13 + i * 0.73 + track.index)
          );
          return (
            <div
              key={i}
              style={{
                width: 4,
                height: 7 + v * 30,
                background: i % 2 ? accent : accent2,
                boxShadow: `0 0 8px ${accent}`,
              }}
            />
          );
        })}
      </div>

      <div
        style={{
          position: "absolute",
          left: 45,
          right: 45,
          bottom: 20,
          height: 3,
          background: "rgba(255,255,255,.14)",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progress}%`,
            background: `linear-gradient(90deg,${accent2},${accent})`,
            boxShadow: `0 0 12px ${accent}`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
