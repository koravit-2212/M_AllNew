import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import AccessKioskPage from '../pages/AccessKioskPage.jsx'

describe('T-03 kiosk shell and API integration', () => {
  it('AC-ACC-01 foundation: กรอกรหัสและสแกนสำเร็จเห็นสถานะยืนยันตัวตน และเรียก API ถูกต้อง', async () => {
    const client = {
      getAccessStatus: vi.fn().mockResolvedValue({ currentOccupancy: 128 }),
      scanAccess: vi.fn().mockResolvedValue({
        allowed: true,
        status: 'approved',
        message: 'ยืนยันตัวตนสำเร็จ',
        memberName: 'สมชาย ใจดี',
        memberId: '64123456',
        scannedAt: '2026-11-12T09:12:00+07:00',
        currentOccupancy: 129,
      }),
    }

    render(<AccessKioskPage client={client} />)

    expect(await screen.findByText('สแกนเข้าห้องสมุด')).toBeTruthy()
    expect(screen.getByText('ผู้ใช้บริการปัจจุบัน 128 คน')).toBeTruthy()

    fireEvent.change(screen.getByLabelText('รหัสบัตร / QR Code'), { target: { value: 'STD-12345' } })
    fireEvent.click(screen.getByRole('button', { name: 'สแกนและยืนยัน' }))

    await waitFor(() => expect(client.scanAccess).toHaveBeenCalledWith({ scanMethod: 'qr', qrCodeOrCardId: 'STD-12345' }))
    expect(await screen.findByText('ยืนยันตัวตนสำเร็จ')).toBeTruthy()
    expect(screen.getByText('สมชาย ใจดี')).toBeTruthy()
    expect(screen.getByText('ผู้ใช้บริการปัจจุบัน 129 คน')).toBeTruthy()
  })

  it('FR-ACC-04 / AC-ACC-03: กรณีอ่านข้อมูลไม่ได้เห็นข้อความแจ้งให้สแกนใหม่และพร้อมสแกนซ้ำ', async () => {
    const client = {
      getAccessStatus: vi.fn().mockResolvedValue({ currentOccupancy: 128 }),
      scanAccess: vi.fn().mockRejectedValue(new Error('scan failed')),
    }

    render(<AccessKioskPage client={client} />)

    fireEvent.change(screen.getByLabelText('รหัสบัตร / QR Code'), { target: { value: 'BAD-SCAN' } })
    fireEvent.click(screen.getByRole('button', { name: 'สแกนและยืนยัน' }))

    expect(await screen.findByText('ไม่สามารถอ่านข้อมูลได้')).toBeTruthy()
    expect(screen.getByText('ระบบจะไม่บันทึกการเข้าใช้บริการ')).toBeTruthy()

    fireEvent.change(screen.getByLabelText('รหัสบัตร / QR Code'), { target: { value: 'STD-12345' } })
    expect(screen.getByText('กรุณาเลือกวิธีสแกนและกรอกรหัสบัตรหรือ QR Code เพื่อเริ่มการยืนยันตัวตน')).toBeTruthy()
  })

  it('FR-ACC-05: กรณีไม่มีสิทธิ์เห็นข้อความปฏิเสธและให้ติดต่อเจ้าหน้าที่', async () => {
    const client = {
      getAccessStatus: vi.fn().mockResolvedValue({ currentOccupancy: 128 }),
      scanAccess: vi.fn().mockRejectedValue({ status: 403, detail: 'ไม่มีสิทธิ์' }),
    }

    render(<AccessKioskPage client={client} />)

    fireEvent.change(screen.getByLabelText('รหัสบัตร / QR Code'), { target: { value: 'STD-1002' } })
    fireEvent.click(screen.getByRole('button', { name: 'สแกนและยืนยัน' }))

    expect((await screen.findAllByText('ไม่มีสิทธิ์')).length).toBeGreaterThan(0)
    expect(screen.getAllByText('กรุณาลองใหม่หรือติดต่อเจ้าหน้าที่').length).toBeGreaterThan(0)
  })
})
