// T-08 (FR-EQP-03, FR-EQP-04, NFR-USB-01) ตรวจด้วย AC-EQP-02
// T-12 (FR-EQP-06, NFR-USB-01) ตรวจด้วย AC-EQP-04
// T-13 (FR-EQP-04, Q-03) ตรวจด้วย AC-EQP-02 (กำหนดคืน)
// T-14 (FR-EQP-06, ASM-02, Q-04) ตรวจด้วย AC-EQP-04 (บล็อกและ override)
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import StaffLoanApprovalPage from '../pages/StaffLoanApprovalPage.jsx'

const PENDING = {
  request_id: 'REQ-0001',
  status: 'pending',
  quantity: 1,
  student: { student_id: 'S1', name: 'นักศึกษาทดสอบ 1' },
  outstanding_items: [],
  equipment: { equipment_type_id: 'A', name: 'อุปกรณ์ทดสอบ', available_count: 3 },
  due_date: '2026-11-13',
}

describe('AC-EQP-02 เจ้าหน้าที่อนุมัติ ระบบบันทึกการยืมและลดจำนวนคงเหลือ', () => {
  it('AC-EQP-02 เห็นนักศึกษา อุปกรณ์ รายการค้างคืนไม่มี กดอนุมัติแล้วเห็นบันทึกการยืมแล้วและคงเหลือใหม่', async () => {
    // Given อุปกรณ์มีจำนวนเพียงพอและนักศึกษาไม่มีรายการค้างคืน
    const client = {
      listPendingLoanRequests: vi
        .fn()
        .mockResolvedValueOnce({ items: [PENDING] })
        .mockResolvedValue({ items: [] }),
      approveLoanRequest: vi.fn().mockResolvedValue({
        loan_id: 'LOAN-0001',
        request_id: 'REQ-0001',
        equipment_name: 'อุปกรณ์ทดสอบ',
        quantity: 1,
        available_count: 2,
      }),
    }
    render(<StaffLoanApprovalPage client={client} />)
    expect(screen.getByRole('heading', { name: 'อนุมัติคำขอยืมอุปกรณ์ (เจ้าหน้าที่)' })).toBeTruthy()

    // เจ้าหน้าที่เปิดคำขอและตรวจข้อมูลนักศึกษา (FR-EQP-03)
    fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ 1/ }))
    const card = within(screen.getByLabelText('ข้อมูลคำขอ'))
    expect(card.getByText('นักศึกษาทดสอบ 1 (S1)')).toBeTruthy()
    expect(card.getByText('อุปกรณ์ทดสอบ × 1')).toBeTruthy()
    expect(card.getByText('รายการค้างคืน')).toBeTruthy()
    expect(card.getByText('ไม่มี')).toBeTruthy()

    // When เจ้าหน้าที่อนุมัติการยืม
    fireEvent.click(screen.getByRole('button', { name: 'อนุมัติการยืม' }))

    // Then ระบบบันทึกการยืมและแสดงจำนวนคงเหลือที่ลดลง
    await waitFor(() => expect(client.approveLoanRequest).toHaveBeenCalledWith('REQ-0001'))
    expect(await screen.findByText('บันทึกการยืมแล้ว')).toBeTruthy()
    expect(screen.getByText('อุปกรณ์ทดสอบคงเหลือ 2')).toBeTruthy()
    expect(screen.queryByRole('button', { name: /นักศึกษาทดสอบ 1/ })).toBeNull()
  })
})

describe('AC-EQP-04 นักศึกษามีรายการค้างคืน เจ้าหน้าที่ต้องตรวจก่อน', () => {
  it('AC-EQP-04 เห็นคำเตือนมีรายการค้างคืน พร้อมรายการที่ค้าง', async () => {
    // Given นักศึกษามีรายการค้างคืนอุปกรณ์หรือหนังสือ
    // When นักศึกษาขอยืมอุปกรณ์เพิ่ม (มีคำขอรอเจ้าหน้าที่)
    const client = {
      listPendingLoanRequests: vi.fn().mockResolvedValue({
        items: [
          {
            ...PENDING,
            request_id: 'REQ-0002',
            student: { student_id: 'S2', name: 'นักศึกษาทดสอบ 2' },
            has_outstanding: true,
            outstanding_items: [
              { item: 'ของค้าง 1', days_overdue: 2 },
              { item: 'ของค้าง 2', days_overdue: 5 },
            ],
          },
        ],
      }),
      approveLoanRequest: vi.fn(),
    }
    render(<StaffLoanApprovalPage client={client} />)
    fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ 2/ }))

    // Then เจ้าหน้าที่ต้องตรวจสอบรายการค้างคืนก่อนตัดสินใจอนุมัติ
    const alert = within(screen.getByRole('alert'))
    expect(alert.getByText('มีรายการค้างคืน')).toBeTruthy()
    expect(alert.getByText('ของค้าง 1 — เกินกำหนด 2 วัน')).toBeTruthy()
    expect(alert.getByText('ของค้าง 2 — เกินกำหนด 5 วัน')).toBeTruthy()
    expect(within(screen.getByLabelText('ข้อมูลคำขอ')).queryByText('ไม่มี')).toBeNull()
    expect(client.approveLoanRequest).not.toHaveBeenCalled()
  })

  it('AC-EQP-04 นักศึกษาไม่มีรายการค้างคืน ไม่เห็นคำเตือน', async () => {
    const client = {
      listPendingLoanRequests: vi.fn().mockResolvedValue({ items: [PENDING] }),
      approveLoanRequest: vi.fn(),
    }
    render(<StaffLoanApprovalPage client={client} />)
    fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ 1/ }))

    expect(screen.queryByText('มีรายการค้างคืน')).toBeNull()
  })
})

describe('AC-EQP-02 กำหนดคืน (due date) ตามประเภทอุปกรณ์', () => {
  it('AC-EQP-02 เห็นกำหนดคืนก่อนอนุมัติ และเห็นกำหนดคืนที่บันทึกหลังอนุมัติ', async () => {
    // Given อุปกรณ์มีพอและนักศึกษาไม่มีรายการค้างคืน
    const client = {
      listPendingLoanRequests: vi.fn().mockResolvedValueOnce({ items: [PENDING] }).mockResolvedValue({ items: [] }),
      approveLoanRequest: vi.fn().mockResolvedValue({
        request_id: 'REQ-0001',
        equipment_name: 'อุปกรณ์ทดสอบ',
        quantity: 1,
        available_count: 2,
        due_date: '2026-11-13',
      }),
    }
    render(<StaffLoanApprovalPage client={client} />)
    fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ 1/ }))
    expect(screen.getByText('กำหนดคืน (due date)')).toBeTruthy()
    expect(screen.getByText(/13 พ\.ย\. 2569/)).toBeTruthy()

    // When เจ้าหน้าที่อนุมัติการยืม
    fireEvent.click(screen.getByRole('button', { name: 'อนุมัติการยืม' }))

    // Then ระบบบันทึกการยืมพร้อมกำหนดคืน
    expect(await screen.findByText('บันทึกการยืมแล้ว')).toBeTruthy()
    const saved = within(screen.getByLabelText('กำหนดคืนที่บันทึก'))
    expect(saved.getByText('กำหนดคืน')).toBeTruthy()
    expect(saved.getByText(/13 พ\.ย\. 2569/)).toBeTruthy()
  })
})

describe('AC-EQP-04 บล็อกการอนุมัติปกติและให้เจ้าหน้าที่ override', () => {
  it('AC-EQP-04 นักศึกษามีรายการค้างคืน ไม่มีปุ่มอนุมัติปกติ กดปลดล็อกแล้วบันทึกการยืม', async () => {
    // Given นักศึกษามีรายการค้างคืน
    // When นักศึกษาขอยืมอุปกรณ์เพิ่ม
    const client = {
      listPendingLoanRequests: vi
        .fn()
        .mockResolvedValueOnce({
          items: [
            {
              ...PENDING,
              request_id: 'REQ-0003',
              student: { student_id: 'S3', name: 'นักศึกษาทดสอบ 3' },
              has_outstanding: true,
              blocked: true,
              outstanding_items: [{ item: 'ของค้าง', days_overdue: 2 }],
            },
          ],
        })
        .mockResolvedValue({ items: [] }),
      approveLoanRequest: vi.fn(),
      overrideLoanRequest: vi.fn().mockResolvedValue({
        request_id: 'REQ-0003',
        equipment_name: 'อุปกรณ์ทดสอบ',
        quantity: 1,
        available_count: 2,
        due_date: '2026-11-13',
        override: true,
      }),
    }
    render(<StaffLoanApprovalPage client={client} />)
    fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ 3/ }))

    // Then เจ้าหน้าที่ตรวจรายการค้างคืน ระบบบล็อกการอนุมัติปกติ (ASM-02)
    expect(screen.getByText('มีรายการค้างคืน')).toBeTruthy()
    expect(screen.getByText('ระบบบล็อกการยืมใหม่จนกว่าจะคืนและชำระค่าปรับ')).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'อนุมัติการยืม' })).toBeNull()

    // เจ้าหน้าที่ตัดสินใจปลดล็อกเป็นกรณีพิเศษ
    fireEvent.click(screen.getByRole('button', { name: 'ปลดล็อก (override) เป็นกรณีพิเศษ' }))
    await waitFor(() => expect(client.overrideLoanRequest).toHaveBeenCalledWith('REQ-0003'))
    expect(client.approveLoanRequest).not.toHaveBeenCalled()
    expect(await screen.findByText('บันทึกการยืมแล้ว')).toBeTruthy()
  })

  it('AC-EQP-04 นักศึกษาไม่มีรายการค้างคืน ไม่มีปุ่ม override', async () => {
    const client = {
      listPendingLoanRequests: vi.fn().mockResolvedValue({ items: [PENDING] }),
      approveLoanRequest: vi.fn(),
      overrideLoanRequest: vi.fn(),
    }
    render(<StaffLoanApprovalPage client={client} />)
    fireEvent.click(await screen.findByRole('button', { name: /นักศึกษาทดสอบ 1/ }))

    expect(screen.getByRole('button', { name: 'อนุมัติการยืม' })).toBeTruthy()
    expect(screen.queryByRole('button', { name: 'ปลดล็อก (override) เป็นกรณีพิเศษ' })).toBeNull()
  })
})
