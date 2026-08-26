import React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import {Audio, Video} from "@remotion/media";

export const LyricVideo: React.FC<any> = ({track}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const introSeconds = Math.max(0, Number(track.introSeconds ?? 0));
  const introFrames = Math.round(introSeconds * fps);
  const outroSeconds = Math.max(0, Number(track.outroSeconds ?? 0));
  const outroFrames = Math.round(outroSeconds * fps);
  const songFrames = Math.round(Math.max(0, Number(track.duration ?? 0)) * fps);
  const outroStartFrame = introFrames + songFrames;
  const songFrame = frame - introFrames;
  const songTime = songFrame / fps;

  const accent = track.theme.accent;
  const accent2 = track.theme.accent2;
  const visualStyle = track.visualStyle ?? "auto";
  const metroStyle = visualStyle === "metro-cinematic";
  const cleanStyle = ["minimal-clean", "podcast", "explainer", "metro-cinematic"].includes(visualStyle);
  const terminalStyle = visualStyle === "terminal-green" || track.layout === "terminal";
  const particleCount = metroStyle ? 5 : cleanStyle ? 8 : terminalStyle ? 14 : 24;

  const activeIndex = songTime >= 0
    ? track.lines.findIndex((line: any) => {
        if (line.suppressFlash) return false;
        const start = Number(line.displayStart ?? line.start);
        const end = Number(line.displayEnd ?? line.end);
        return songTime >= start && songTime <= end;
      })
    : -1;

  const active = activeIndex >= 0 ? track.lines[activeIndex] : null;
  const previous = activeIndex > 0 ? track.lines[activeIndex - 1] : null;
  const next =
    activeIndex >= 0 && activeIndex + 1 < track.lines.length
      ? track.lines[activeIndex + 1]
      : null;

  const progress = Math.min(
    100,
    Math.max(0, (songTime / Math.max(track.duration, 0.01)) * 100)
  );

  const zoom = 1.045 + Math.sin(frame / 95) * 0.018;
  const introCoverZoom = interpolate(
    frame,
    [0, Math.max(1, introFrames)],
    [1.02, 1.12],
    {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
  );
  const introOpacity = introFrames > 0
    ? interpolate(
        frame,
        [0, Math.min(12, introFrames * 0.18), Math.max(1, introFrames - 18), introFrames],
        [0, 1, 1, 0],
        {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
      )
    : 0;
  const contentOpacity = introFrames > 0
    ? interpolate(
        frame,
        [Math.max(0, introFrames - 12), introFrames + 12],
        [0, 1],
        {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
      )
    : 1;
  const outroProgress = outroFrames > 0
    ? Math.max(0, Math.min(1, (frame - outroStartFrame) / Math.max(1, outroFrames)))
    : 0;
  const outroOpacity = outroFrames > 0
    ? interpolate(
        frame,
        [outroStartFrame - 10, outroStartFrame + 12],
        [0, 1],
        {extrapolateLeft: "clamp", extrapolateRight: "clamp"}
      )
    : 0;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: cleanStyle ? "#090b10" : "#020306",
        color: "white",
        overflow: "hidden",
        fontFamily: track.layout === "terminal" ? "monospace" : "Arial, Helvetica, sans-serif",
      }}
    >
      <Sequence from={introFrames}>
        <Audio src={staticFile(track.audio)} volume={track.musicVolume ?? 1} />
        {track.voiceover ? (
          <Audio src={staticFile(track.voiceover)} volume={track.voiceoverVolume ?? 1} />
        ) : null}
      </Sequence>

      <AbsoluteFill style={{opacity: contentOpacity}}>
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
        ) : track.cover && track.imageMode === "background" ? (
          <Img
            src={staticFile(track.cover)}
            style={{
              position: "absolute",
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${zoom})`,
              filter: metroStyle ? "blur(3px) brightness(.40) saturate(.82) contrast(1.08)" : "blur(8px) brightness(.30) contrast(1.2)",
            }}
          />
        ) : null}

        {track.cover && track.imageMode === "card" ? (
          <Img
            src={staticFile(track.cover)}
            style={{
              position: "absolute",
              left: "50%",
              top: "13%",
              width: "46%",
              height: "36%",
              objectFit: "contain",
              transform: "translateX(-50%)",
              filter: "drop-shadow(0 18px 40px rgba(0,0,0,.6))",
            }}
          />
        ) : null}

        {track.cover && track.imageMode === "logo" ? (
          <Img
            src={staticFile(track.cover)}
            style={{position: "absolute", right: 38, top: 72, width: 135, height: 135, objectFit: "contain", zIndex: 5}}
          />
        ) : null}

        <AbsoluteFill
          style={{
            background: metroStyle
              ? `linear-gradient(90deg, rgba(0,0,0,.64), rgba(0,0,0,.16) 45%, rgba(0,0,0,.58)), linear-gradient(180deg, rgba(0,0,0,.08), rgba(0,0,0,.76))`
              : `
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

        {Array.from({length: particleCount}).map((_, i) => {
          const x = (i * 73 + track.index * 11) % 100;
          const y = 110 - ((i * 41 + frame * (0.035 + (i % 4) * 0.01)) % 115);
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
            opacity: metroStyle ? 0.02 : cleanStyle ? 0.10 : terminalStyle ? 0.24 : 0.34,
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
            opacity: metroStyle ? 0.035 : cleanStyle ? 0.025 : terminalStyle ? 0.12 : 0.08,
            background: "repeating-linear-gradient(0deg,transparent 0px,transparent 3px,rgba(255,255,255,.12) 4px)",
          }}
        />

        {metroStyle ? (
          <>
            <div style={{position: "absolute", left: "-10%", right: "-10%", top: "18%", height: 2, opacity: 0.28, background: `linear-gradient(90deg, transparent, ${accent}, transparent)`, transform: `translateX(${Math.sin(frame / 21) * 12}%)`, filter: "blur(1px)"}} />
            <div style={{position: "absolute", left: "-10%", right: "-10%", bottom: "24%", height: 1, opacity: 0.18, background: `linear-gradient(90deg, transparent, ${accent2}, transparent)`, transform: `translateX(${Math.cos(frame / 27) * 16}%)`}} />
          </>
        ) : null}

        <div
          style={{
            position: "absolute",
            left: 45,
            top: 34,
            fontWeight: 850,
            fontSize: 15,
            letterSpacing: 5,
            zIndex: 10,
          }}
        >
          <span style={{color: accent}}>●</span>{" "}
          {(track.brand || "RICHMACK RADIO").toUpperCase()}
        </div>

        <div
          style={{
            position: "absolute",
            right: 45,
            top: 31,
            textAlign: "right",
            zIndex: 10,
            maxWidth: "36%",
          }}
        >
          <div style={{fontSize: 15, fontWeight: 900, letterSpacing: 2.2, textTransform: "uppercase"}}>
            {track.title}
          </div>
          {track.artist ? (
            <div style={{marginTop: 5, fontSize: 13, color: accent, letterSpacing: 2, textTransform: "uppercase"}}>
              {track.artist}
            </div>
          ) : null}
        </div>

        {!metroStyle && previous && previous.section === active?.section && (
          <div
            style={{
              position: "absolute",
              top: "24%",
              left: 90,
              right: 90,
              textAlign: "center",
              opacity: 0.14,
              fontSize: 20,
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
            padding: "120px 65px 95px",
          }}
        >
          {active && (
            <div style={{maxWidth: 1110}}>
              {active.section ? (
                <div
                  style={{
                    display: "inline-block",
                    marginBottom: 26,
                    padding: "8px 18px",
                    border: `1px solid ${accent}66`,
                    borderRadius: 999,
                    color: accent,
                    background: "rgba(0,0,0,.35)",
                    fontSize: 15,
                    fontWeight: 800,
                    letterSpacing: 3,
                    textTransform: "uppercase",
                    boxShadow: `0 0 18px ${accent}22`,
                  }}
                >
                  [ {active.section} ]
                </div>
              ) : null}

              <div
                style={{
                  fontSize: metroStyle ? (active.text.length > 65 ? 42 : active.text.length > 45 ? 50 : 58) : active.text.length > 65 ? 43 : active.text.length > 45 ? 51 : 61,
                  lineHeight: 1.15,
                  fontWeight: 950,
                  textTransform: metroStyle ? "none" : "uppercase",
                  textShadow: metroStyle ? "0 5px 24px rgba(0,0,0,.9)" : "0 8px 28px rgba(0,0,0,.95)",
                }}
              >
                {active.words.map((word: any, i: number) => {
                  const started = songTime >= word.start;
                  const current = songTime >= word.start && songTime <= word.end;
                  const duration = Math.max(0.04, word.end - word.start);
                  const wordProgress = Math.max(0, Math.min(1, (songTime - word.start) / duration));

                  return (
                    <span
                      key={`${word.start}-${i}`}
                      style={{
                        display: "inline-block",
                        position: "relative",
                        marginRight: 14,
                        marginBottom: 11,
                        color: current ? accent : started ? "#fff" : "rgba(255,255,255,.27)",
                        transform: current ? "translateY(-5px) scale(1.06)" : "scale(1)",
                        textShadow: current ? `0 0 10px ${accent}, 0 0 30px ${accent}, 0 0 55px ${accent2}` : undefined,
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

              {!metroStyle && next && next.section === active.section && (
                <div style={{marginTop: 30, fontSize: 25, opacity: 0.28}}>{next.text}</div>
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
            const v = Math.abs(Math.sin(frame * 0.13 + i * 0.73 + track.index));
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

      {introFrames > 0 && track.cover ? (
        <AbsoluteFill style={{opacity: introOpacity, backgroundColor: "#020306", zIndex: 50}}>
          <Img
            src={staticFile(track.cover)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${introCoverZoom})`,
              filter: "brightness(.72) saturate(1.12) contrast(1.08)",
            }}
          />
          <AbsoluteFill
            style={{
              background: `linear-gradient(180deg, rgba(0,0,0,.08), rgba(0,0,0,.26)), radial-gradient(circle at 50% 50%, transparent 48%, ${accent}22 100%)`,
              boxShadow: `inset 0 0 120px ${accent2}22`,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: 45,
              top: 34,
              fontWeight: 850,
              fontSize: 15,
              letterSpacing: 5,
              textShadow: "0 2px 16px rgba(0,0,0,.9)",
            }}
          >
            <span style={{color: accent}}>●</span>{" "}
            {(track.brand || "RICHMACK RADIO").toUpperCase()}
          </div>
        </AbsoluteFill>
      ) : null}

      {outroFrames > 0 && frame >= outroStartFrame ? (
        <AbsoluteFill style={{opacity: outroOpacity, backgroundColor: "#020306", zIndex: 60, alignItems: "center", justifyContent: "center"}}>
          {track.outroImage ? (
            <Img
              src={staticFile(track.outroImage)}
              style={{position: "absolute", width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.04 + outroProgress * 0.05})`, filter: "brightness(.34) saturate(.9) blur(2px)"}}
            />
          ) : null}
          <AbsoluteFill style={{background: "linear-gradient(180deg,rgba(0,0,0,.2),rgba(0,0,0,.78))"}} />
          <div style={{zIndex: 2, textAlign: "center", padding: 60}}>
            <div style={{fontSize: 15, fontWeight: 850, letterSpacing: 5, marginBottom: 22}}><span style={{color: accent}}>●</span> {(track.brand || "RICHMACK RADIO").toUpperCase()}</div>
            <div style={{fontSize: 48, fontWeight: 900, letterSpacing: 1, textShadow: "0 6px 28px rgba(0,0,0,.9)"}}>{track.outroText || "Thanks for listening"}</div>
            <div style={{marginTop: 18, fontSize: 18, color: accent, letterSpacing: 3, textTransform: "uppercase"}}>{track.artist || ""}</div>
          </div>
        </AbsoluteFill>
      ) : null}
    </AbsoluteFill>
  );
};
