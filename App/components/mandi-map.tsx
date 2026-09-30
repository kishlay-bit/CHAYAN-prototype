'use client'
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import { useEffect } from 'react'

type Mandi = readonly [string, number, number, string, string, string, string, number]
const icon = (privateCentre:boolean) => L.divIcon({className:'custom-pin', html:`<span class="map-pin ${privateCentre?'private-pin':'gov-pin'}"></span>`, iconSize:[22,28], iconAnchor:[11,28]})
export default function MandiMap({mandis,onSelect}:{mandis:Mandi[];onSelect:(m:Mandi)=>void}) { return <div className="leaflet-wrap"><MapContainer center={[21.1458,79.0882]} zoom={9} scrollWheelZoom={false} zoomControl={true} className="leaflet-map"><TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>{mandis.map(m=><Marker key={m[0]} position={[m[1],m[2]]} icon={icon(m[3]==='Private')} eventHandlers={{click:()=>onSelect(m)}}><Popup><b>{m[0]}</b><br/>{m[3]} centre<br/>{m[4]}</Popup></Marker>)}</MapContainer></div> }
