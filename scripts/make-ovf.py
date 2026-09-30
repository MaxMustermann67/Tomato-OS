#!/usr/bin/env python3
"""Write an OVF descriptor for the stream-optimized VMDK."""
import sys
from pathlib import Path
from xml.sax.saxutils import escape

disk = Path(sys.argv[1])
target = Path(sys.argv[2])
if not disk.is_file():
    raise SystemExit("VMDK missing")
name = escape(disk.name)
size = disk.stat().st_size
xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="http://schemas.dmtf.org/ovf/envelope/1"
          xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1"
          xmlns:rasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData"
          xmlns:vssd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData">
  <References><File ovf:id="file1" ovf:href="{name}" ovf:size="{size}"/></References>
  <DiskSection>
    <Info>Virtual disks</Info>
    <Disk ovf:diskId="disk1" ovf:fileRef="file1" ovf:capacity="{16 * 1024 ** 3}"
          ovf:format="http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized"/>
  </DiskSection>
  <NetworkSection>
    <Info>Virtual networks</Info>
    <Network ovf:name="NAT"><Description>Internet access through VirtualBox NAT</Description></Network>
  </NetworkSection>
  <VirtualSystem ovf:id="Tomaten-OS">
    <Info>Tomaten OS virtual machine</Info>
    <Name>Tomaten OS</Name>
    <OperatingSystemSection ovf:id="101">
      <Info>Debian GNU/Linux 64-bit</Info>
      <Description>Debian_64</Description>
    </OperatingSystemSection>
    <VirtualHardwareSection>
      <Info>Virtual hardware requirements</Info>
      <System>
        <vssd:ElementName>Tomaten OS</vssd:ElementName>
        <vssd:InstanceID>0</vssd:InstanceID>
        <vssd:VirtualSystemIdentifier>Tomaten OS</vssd:VirtualSystemIdentifier>
        <vssd:VirtualSystemType>virtualbox-2.2</vssd:VirtualSystemType>
      </System>
      <Item><rasd:Caption>2 virtual CPUs</rasd:Caption><rasd:InstanceID>1</rasd:InstanceID><rasd:ResourceType>3</rasd:ResourceType><rasd:VirtualQuantity>2</rasd:VirtualQuantity></Item>
      <Item><rasd:Caption>4096 MB RAM</rasd:Caption><rasd:InstanceID>2</rasd:InstanceID><rasd:ResourceType>4</rasd:ResourceType><rasd:VirtualQuantity>4096</rasd:VirtualQuantity><rasd:AllocationUnits>byte * 2^20</rasd:AllocationUnits></Item>
      <Item><rasd:Caption>IDE controller</rasd:Caption><rasd:InstanceID>3</rasd:InstanceID><rasd:ResourceType>5</rasd:ResourceType></Item>
      <Item><rasd:Caption>Tomaten OS disk</rasd:Caption><rasd:InstanceID>4</rasd:InstanceID><rasd:ResourceType>17</rasd:ResourceType><rasd:HostResource>ovf:/disk/disk1</rasd:HostResource><rasd:Parent>3</rasd:Parent><rasd:AddressOnParent>0</rasd:AddressOnParent></Item>
      <Item><rasd:Caption>Network adapter</rasd:Caption><rasd:InstanceID>5</rasd:InstanceID><rasd:ResourceType>10</rasd:ResourceType><rasd:ResourceSubType>E1000</rasd:ResourceSubType><rasd:Connection>NAT</rasd:Connection><rasd:AutomaticAllocation>true</rasd:AutomaticAllocation></Item>
    </VirtualHardwareSection>
  </VirtualSystem>
</Envelope>
'''
target.write_text(xml, encoding="utf-8")