"use client";

import { useEffect, useId, useRef, useState } from "react";

const months = Array.from({ length: 12 }, (_, month) =>
  new Intl.DateTimeFormat("pt-BR", { month: "long", timeZone: "UTC" }).format(new Date(Date.UTC(2026, month, 1))),
);
const weekdays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
const pad = (value: number) => String(value).padStart(2, "0");
const display = (value: string) => value.split("-").reverse().join("/");

function toIso(text: string) {
  const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(text);
  if (!match) return "";
  const iso = [match[3], match[2], match[1]].join("-");
  const date = new Date(iso + "T00:00:00Z");
  return Number(match[3]) > 0 && Number.isFinite(date.valueOf()) && date.toISOString().slice(0, 10) === iso ? iso : "";
}

export default function DateField({ label, name, min, max, onDateChange }: {
  label: string;
  name: string;
  min?: string;
  max: string;
  onDateChange?: (value: string) => void;
}) {
  const id = useId();
  const input = useRef<HTMLInputElement>(null);
  const [text, setText] = useState("");
  const [open, setOpen] = useState(false);
  const [view, setView] = useState(max.slice(0, 7));
  const iso = toIso(text);
  const [year, month] = view.split("-").map(Number);
  const start = new Date(view + "-01T00:00:00Z").getUTCDay();
  const last = new Date(Date.UTC(year, month, 0)).getUTCDate();
  const minYear = min ? Number(min.slice(0, 4)) : Math.min(1900, year);
  const maxYear = Number(max.slice(0, 4));

  useEffect(() => {
    let message = "";
    if (text && !iso) message = "Informe uma data válida no formato DD/MM/AAAA.";
    else if (iso && min && iso < min) message = "Informe uma data a partir de " + display(min) + ".";
    else if (iso && iso > max) message = "Informe uma data até " + display(max) + ".";
    input.current?.setCustomValidity(message);
  }, [text, iso, min, max]);

  function update(value: string) {
    setText(value);
    onDateChange?.(toIso(value));
  }

  function move(offset: number) {
    const next = new Date(Date.UTC(year, month - 1 + offset, 1));
    setView(next.toISOString().slice(0, 7));
  }

  return (
    <div className="date-field" onBlur={(event) => {
      if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false);
    }} onKeyDown={(event) => {
      if (event.key === "Escape" && open) { setOpen(false); input.current?.focus(); }
    }}>
      <label htmlFor={id}>{label} <span>*</span></label>
      <div className="date-control">
        <input id={id} ref={input} required inputMode="numeric" placeholder="DD/MM/AAAA" maxLength={10} value={text}
          onChange={(event) => {
            const digits = event.target.value.replace(/\D/g, "").slice(0, 8);
            update([digits.slice(0, 2), digits.slice(2, 4), digits.slice(4)].filter(Boolean).join("/"));
          }} />
        <input type="hidden" name={name} value={iso} />
        <button type="button" className="calendar-toggle" aria-label={"Calendário: " + label} aria-expanded={open} aria-controls={id + "-calendar"} onClick={() => {
          if (!open) {
            const today = new Date().toISOString().slice(0, 10);
            const date = iso || today;
            setView((date > max ? max : min && date < min ? min : date).slice(0, 7));
          }
          setOpen(!open);
        }}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="3"/><path d="M7 3v5m10-5v5M3 10h18"/></svg>
        </button>
      </div>
      {open && <div className="calendar-popover" id={id + "-calendar"} role="group" aria-label={label}>
        <div className="calendar-toolbar">
          <button type="button" aria-label="Mês anterior" disabled={view <= (min?.slice(0, 7) ?? "1900-01") || year <= 99} onClick={() => move(-1)}>‹</button>
          <select aria-label="Mês" value={month} onChange={(event) => setView(String(year).padStart(4, "0") + "-" + pad(Number(event.target.value)))}>
            {months.map((item, index) => {
              const candidate = String(year).padStart(4, "0") + "-" + pad(index + 1);
              return <option key={item} value={index + 1} disabled={candidate > max.slice(0, 7) || !!min && candidate < min.slice(0, 7)}>{item}</option>;
            })}
          </select>
          <select aria-label="Ano" value={year} onChange={(event) => {
            const candidate = event.target.value.padStart(4, "0") + "-" + pad(month);
            setView(candidate > max.slice(0, 7) ? max.slice(0, 7) : min && candidate < min.slice(0, 7) ? min.slice(0, 7) : candidate);
          }}>
            {Array.from({ length: maxYear - minYear + 1 }, (_, index) => maxYear - index).map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
          <button type="button" aria-label="Próximo mês" disabled={view >= max.slice(0, 7)} onClick={() => move(1)}>›</button>
        </div>
        <div className="calendar-grid">
          {weekdays.map((day) => <span className="calendar-weekday" key={day}>{day}</span>)}
          {Array.from({ length: start }, (_, index) => <span key={"blank-" + index} />)}
          {Array.from({ length: last }, (_, index) => {
            const day = index + 1;
            const value = view + "-" + pad(day);
            return <button key={day} type="button" aria-label={display(value)} aria-pressed={iso === value} disabled={value > max || !!min && value < min} onClick={() => {
              update(display(value));
              setOpen(false);
              input.current?.focus();
            }}>{day}</button>;
          })}
        </div>
      </div>}
    </div>
  );
}
