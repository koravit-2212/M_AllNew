// T-04 (FR-EQP-01, NFR-USB-01) ตรวจด้วย AC-EQP-01
// T-07 (FR-EQP-02, ASM-01, NFR-USB-01) ตรวจด้วย AC-EQP-02
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

import EquipmentLoanPage from '../pages/EquipmentLoanPage.jsx'

const STUDENTS = [
  { student_id: 'S1', name: 'นักศึกษาทดสอบ 1' },
  { student_id: 'S2', name: 'นักศึกษาทดสอบ 2' },
]

function makeClient(items) {
  return {
    listEquipmentTypes: vi.fn().mockResolvedValue({ items }),
    listStudents: vi.fn().mockResolvedValue({ items: STUDENTS }),
    createLoanRequest: vi.fn().mockResolvedValue({ request_id: 'REQ-0001', status: 'pending', quantity: 1 }),
  }
}

describe('AC-EQP-01 นักศึกษาเห็นประเภทอุปกรณ์ที่ยืมได้', () => {
  it('AC-EQP-01 แสดงชื่ออุปกรณ์ จำนวนคงเหลือ และป้ายว่าง ให้เลือก', async () => {
    // Given มีรายการอุปกรณ์ให้บริการในระบบ
    const client = makeClient([
      { equipment_type_id: 'A', name: 'อุปกรณ์ทดสอบ 1', available_count: 3 },
      { equipment_type_id: 'B', name: 'อุปกรณ์ทดสอบ 2', available_count: 1 },
    ])

    // When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
    render(<EquipmentLoanPage client={client} />)

    // Then ระบบแสดงประเภทอุปกรณ์ที่สามารถยืมได้ให้เลือก
    expect(await screen.findByText('อุปกรณ์ทดสอบ 1')).toBeTruthy()
    expect(screen.getByText('อุปกรณ์ทดสอบ 2')).toBeTruthy()
    expect(screen.getByText('คงเหลือ 3')).toBeTruthy()
    expect(screen.getByText('คงเหลือ 1')).toBeTruthy()
    expect(screen.getAllByText('ว่าง')).toHaveLength(2)
    expect(screen.getByText('เลือกอุปกรณ์')).toBeTruthy()
    expect(client.listEquipmentTypes).toHaveBeenCalledTimes(1)

    const option = screen.getByRole('button', { name: /อุปกรณ์ทดสอบ 1/ })
    expect(option.getAttribute('aria-pressed')).toBe('false')
    fireEvent.click(option)
    expect(option.getAttribute('aria-pressed')).toBe('true')
  })
})

describe('AC-EQP-02 นักศึกษาส่งคำขอยืมให้เจ้าหน้าที่อนุมัติ', () => {
  it('AC-EQP-02 เลือกอุปกรณ์ กดส่งคำขอยืม แล้วเห็นส่งคำขอแล้ว รอเจ้าหน้าที่', async () => {
    // Given อุปกรณ์ที่ต้องการมีจำนวนเพียงพอ และเลือกนักศึกษาตัวอย่างได้
    const client = makeClient([{ equipment_type_id: 'A', name: 'อุปกรณ์ทดสอบ 1', available_count: 3 }])
    render(<EquipmentLoanPage client={client} />)
    await screen.findByText('อุปกรณ์ทดสอบ 1')
    await screen.findByRole('option', { name: /นักศึกษาทดสอบ 2/ })

    const submit = screen.getByRole('button', { name: 'ส่งคำขอยืม' })
    expect(submit.disabled).toBe(true)
    expect(screen.getByText('เจ้าหน้าที่จะตรวจสอบและอนุมัติคำขอก่อนยืมเสมอ')).toBeTruthy()

    // When นักศึกษาเลือกอุปกรณ์และกดส่งคำขอยืม
    fireEvent.change(screen.getByLabelText('นักศึกษา'), { target: { value: 'S2' } })
    fireEvent.click(screen.getByRole('button', { name: /อุปกรณ์ทดสอบ 1/ }))
    expect(submit.disabled).toBe(false)
    fireEvent.click(submit)

    // Then ระบบส่งคำขอ และแสดงว่ารอเจ้าหน้าที่ตรวจสอบและอนุมัติ (ASM-01)
    await waitFor(() => {
      expect(client.createLoanRequest).toHaveBeenCalledWith({ studentId: 'S2', equipmentTypeId: 'A', quantity: 1 })
    })
    expect(await screen.findByText('ส่งคำขอแล้ว')).toBeTruthy()
    expect(screen.getByText('รอเจ้าหน้าที่ตรวจสอบและอนุมัติ')).toBeTruthy()
    expect(screen.getByText('อุปกรณ์ทดสอบ 1 × 1')).toBeTruthy()
  })
})
