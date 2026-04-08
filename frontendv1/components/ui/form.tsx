"use client";

import type { DefaultValues, FieldPath, FieldValues, SubmitHandler } from "react-hook-form";
import type { ZodSchema } from "zod";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/components/ui/button";
import { InlineValidationMessage } from "@/components/ui/inline-validation-message";

interface FormFieldProps<T extends FieldValues> {
  name: FieldPath<T>;
  label: string;
  required?: boolean;
  placeholder?: string;
}

interface FormProps<T extends FieldValues> {
  schema: ZodSchema<T>;
  defaultValues: DefaultValues<T>;
  onSubmit: SubmitHandler<T>;
  children: React.ReactNode;
  submitLabel?: string;
  className?: string;
}

export function Form<T extends FieldValues>({
  schema,
  defaultValues,
  onSubmit,
  children,
  submitLabel = "Submit",
  className,
}: FormProps<T>) {
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm<T>({
    resolver: zodResolver(schema),
    defaultValues,
  });

  return (
    <form className={className} onSubmit={handleSubmit(onSubmit)}>
      {children}
      <div className="mt-6">
        <Button
          type="submit"
          variant="primary"
          disabled={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? "Submitting..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}

export function FormField<T extends FieldValues>({
  name,
  label,
  required,
  placeholder,
  type = "text",
  className,
}: FormFieldProps<T> & {
  type?: string;
  className?: string;
}) {
  // This is a simple text field - extend for other field types as needed
  return (
    <div className={className}>
      <label htmlFor={name} className="mb-1.5 block text-sm font-medium text-ink-800">
        {label}
        {required && <span className="text-ember ml-0.5">*</span>}
      </label>
      <input
        type={type}
        id={name}
        placeholder={placeholder}
        className="w-full rounded-full border border-black/10 bg-white/80 px-4 py-3 text-sm transition placeholder:text-ink-300 focus:border-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900/10 disabled:cursor-not-allowed disabled:opacity-60"
      />
    </div>
  );
}

// Generic input field component for use with react-hook-form
interface InputFieldProps<T extends FieldValues> {
  name: FieldPath<T>;
  label: string;
  form: ReturnType<typeof useForm<T>>;
  required?: boolean;
  placeholder?: string;
  type?: string;
}

export function InputField<T extends FieldValues>({
  name,
  label,
  form,
  required,
  placeholder,
  type = "text",
}: InputFieldProps<T>) {
  const error = form.formState.errors[name];

  return (
    <div>
      <label htmlFor={name} className="mb-1.5 block text-sm font-medium text-ink-800">
        {label}
        {required && <span className="text-ember ml-0.5">*</span>}
      </label>
      <input
        type={type}
        id={name}
        placeholder={placeholder}
        {...form.register(name)}
        className="w-full rounded-full border border-black/10 bg-white/80 px-4 py-3 text-sm transition placeholder:text-ink-300 focus:border-ink-900 focus:outline-none focus:ring-2 focus:ring-ink-900/10 disabled:cursor-not-allowed disabled:opacity-60"
      />
      {error && <InlineValidationMessage message={String(error.message)} />}
    </div>
  );
}
